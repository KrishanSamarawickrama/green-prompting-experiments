import argparse, json, re, sys
from pathlib import Path
from datetime import datetime
import yaml
from harness.ollama_client import generate as ollama_generate

def read(path): 
    return Path(path).read_text(encoding="utf-8")

def build_prompt(template_path: str, task_spec_path: str) -> str:
    tpl = read(template_path)
    spec = read(task_spec_path)
    return tpl.replace("{{TASK_SPEC}}", spec)

# --- Robust extractors ---
FENCE_PATTERNS = [
    r"```python\s*(.*?)\s*```",
    r"```py\s*(.*?)\s*```",
    r"```\s*(.*?)\s*```",
    r"~~~python\s*(.*?)\s*~~~",
    r"~~~\s*(.*?)\s*~~~",
]

def extract_python_code_any(text: str) -> str | None:
    for pat in FENCE_PATTERNS:
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if m:
            code = m.group(1).strip()
            if "def run_task" in code:
                return code
            # If fenced but no run_task, still return code (may be helper + fn at end)
            return code

    # Fallback: find a region starting at run_task
    m = re.search(r"(^|\n)\s*def\s+run_task\s*\(", text)
    if m:
        start = m.start()
        code = text[start:].strip()
        # Strip trailing markdown chatter if any closing ticks appear later
        code = re.split(r"\n```|^```", code, maxsplit=1, flags=re.MULTILINE)[0]
        return code.strip()

    return None

def slugify(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", s).strip("_")

def save_debug_raw(content: str, out_dir: Path, stem: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"{stem}.raw.txt"
    p.write_text(content, encoding="utf-8")
    return p

def generate_once(model: str, prompt: str, options: dict | None):
    return ollama_generate(model, prompt, options=options)

def repair_prompt(original_response: str) -> str:
    return (
        "You previously returned code without a clean Python fenced block.\n"
        "Rewrite ONLY as a single fenced Python block that defines run_task(...), with no extra text.\n\n"
        "Example format:\n```python\n# code here\n```\n\n"
        "Here is your previous reply to fix:\n\n"
        f"{original_response}\n"
    )

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-id", required=True, choices=["inefficient_sort","modular_example","unit_test_gen"])
    ap.add_argument("--prompt", required=True,
                    choices=["baseline","cot_then_optimize","eff_from_scratch","tagged_explained"])
    ap.add_argument("--model", default="deepseek-coder:6.7b")
    ap.add_argument("--options", default=None, help="YAML string to override default Ollama options")
    ap.add_argument("--with-codecarbon", action="store_true",
                    help="Log inference energy/CO2e with CodeCarbon during generation")
    ap.add_argument("--retry", type=int, default=1, help="If extraction fails, retry this many times with a repair prompt")
    ap.add_argument("--save-raw", action="store_true", help="Save raw model responses for debugging")
    args = ap.parse_args()

    template = f"prompts/{args.prompt}.txt"
    spec = f"tasks/task_specs/{args.task_id}.md"

    # build prompt
    tpl_text = read(template)
    spec_text = read(spec)
    prompt = tpl_text.replace("{{TASK_SPEC}}", spec_text)

    # options
    options = None
    if args.options:
        options = yaml.safe_load(args.options)

    # run generation (with optional CodeCarbon)
    def _call_model(p):
        if args.with_codecarbon:
            from codecarbon import EmissionsTracker
            tracker = EmissionsTracker(project_name="llm_generation", output_dir="data/raw", log_level="error")
            tracker.start()
            try:
                return ollama_generate(args.model, p, options=options)
            finally:
                emissions = tracker.stop()
                import time
                Path("data/raw").mkdir(parents=True, exist_ok=True)
                with open("data/raw/codecarbon_generation.jsonl","a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "ts": time.time(),
                        "task_id": args.task_id,
                        "prompt": args.prompt,
                        "model": args.model,
                        "options": options,
                        "emissions_kg": emissions
                    }) + "\n")
        else:
            return ollama_generate(args.model, p, options=options)

    resp = _call_model(prompt)
    txt = resp.get("response","")

    if args.save_raw:
        save_debug_raw(txt, Path("data/raw"), f"{args.task_id}__{args.prompt}__{slugify(args.model)}")

    code = extract_python_code_any(txt)
    tries_left = args.retry
    while code is None and tries_left > 0:
        # ask the model to repair the formatting
        fix = repair_prompt(txt)
        resp2 = _call_model(fix)
        txt2 = resp2.get("response","")
        if args.save_raw:
            save_debug_raw(txt2, Path("data/raw"), f"{args.task_id}__{args.prompt}__{slugify(args.model)}__repair{tries_left}")
        code = extract_python_code_any(txt2)
        txt = txt2
        tries_left -= 1

    if not code:
        # Last-ditch: if there's at least some code-ish content, wrap it
        if "def run_task" in txt:
            code = extract_python_code_any(txt) or txt
        else:
            sys.stderr.write("Failed to extract Python code block from model response.\n")
            sys.exit(1)

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
