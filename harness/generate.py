import argparse, json, re
from pathlib import Path
from datetime import datetime
import yaml

from harness.ollama_client import generate as ollama_generate

def read(path): return Path(path).read_text(encoding="utf-8")

def build_prompt(template_path: str, task_spec_path: str) -> str:
    tpl = read(template_path)
    spec = read(task_spec_path)
    return tpl.replace("{{TASK_SPEC}}", spec)

def extract_python_code(text: str) -> str | None:
    # Look for fenced code block
    m = re.search(r"```python\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # Fallback: raw text if it looks like Python
    if "def run_task" in text:
        return text.strip()
    return None

def slugify(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+","_", s).strip("_")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-id", required=True, choices=["inefficient_sort","modular_example"])
    ap.add_argument("--prompt", required=True,
                    choices=["baseline","cot_then_optimize","eff_from_scratch","tagged_explained"])
    ap.add_argument("--model", default="llama3:8b-instruct-q4_K_M")
    ap.add_argument("--options", default=None, help="YAML for Ollama options override")
    args = ap.parse_args()

    template = f"prompts/{args.prompt}.txt"
    spec = f"tasks/task_specs/{args.task_id}.md"

    options = None
    if args.options:
        options = yaml.safe_load(args.options)

    prompt = build_prompt(template, spec)
    resp = ollama_generate(args.model, prompt, options=options)
    txt = resp.get("response","")

    code = extract_python_code(txt)
    if not code:
        raise SystemExit("Failed to extract Python code block from model response.")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{args.task_id}__{args.prompt}__{slugify(args.model)}__{ts}.py"
    out_dir = Path("tasks/generated") / args.task_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / fname
    out_path.write_text(code, encoding="utf-8")

    meta = {
        "task_id": args.task_id,
        "prompt": args.prompt,
        "model": args.model,
        "options": options,
        "timestamp": ts,
        "file": str(out_path)
    }
    (out_dir / (fname + ".json")).write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Saved: {out_path}")
