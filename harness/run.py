import argparse, tracemalloc, time, subprocess, csv, sys, math
from pathlib import Path
from importlib import import_module

from tasks.validators import validate
from harness.utils import parse_perf_stderr, FLOPS_EVENT, latest_generated_module

DATA_FILE = Path("data/derived/runs.csv")
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_module(module_path: str):
    return import_module(module_path)

def run_with_tracemalloc(mod):
    tracemalloc.start()
    t0 = time.perf_counter()
    res = mod.run_task()
    dt = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return dt, peak/1024  # KiB

def run_with_perf(mod):
    cmd = [
        "perf", "stat", "-e", FLOPS_EVENT,
        sys.executable, "-c", f"import importlib; m=importlib.import_module('{mod.__name__}'); m.run_task()"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return parse_perf_stderr(result.stderr)

def append_csv(row: dict):
    new = not DATA_FILE.exists()
    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if new:
            writer.writerow(["task_id","impl","variant","run_idx","runtime_s","mem_kib","flops","energy_j","correct"])
        writer.writerow([row[k] for k in ["task_id","impl","variant","run_idx","runtime_s","mem_kib","flops","energy_j","correct"]])

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-id", required=True, choices=["inefficient_sort","modular_example"])
    ap.add_argument("--impl", required=True, help="Module path. Use tasks.generated.<task>.AUTO_PICK to select latest.")
    ap.add_argument("--variant", default="candidate")
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--energy", type=float, default=0.0, help="Energy in Joules (per-run unless --energy-total).")
    ap.add_argument("--energy-total", action="store_true", help="Treat --energy as total for all runs.")
    ap.add_argument("--skip-perf", action="store_true", help="Skip FLOPs measurement if perf missing.")
    args = ap.parse_args()

    impl = args.impl
    if impl.endswith(".AUTO_PICK"):
        # e.g., tasks.generated.inefficient_sort.AUTO_PICK
        task = args.task_id
        mod = latest_generated_module(task)
        if not mod:
            raise SystemExit(f"No generated module found for task {task}.")
        impl = mod

    mod = load_module(impl)
    correct = 1 if validate(args.task_id, impl) else 0

    per_run_energy = args.energy
    if args.energy_total and args.runs > 0:
        per_run_energy = args.energy / args.runs

    for i in range(args.runs):
        runtime, peak = run_with_tracemalloc(mod)
        flops = None
        if not args.skip_perf:
            try:
                flops = run_with_perf(mod)
            except Exception:
                flops = None
        row = dict(
            task_id=args.task_id, impl=impl, variant=args.variant, run_idx=i,
            runtime_s=runtime, mem_kib=peak, flops=flops if flops is not None else "",
            energy_j=per_run_energy, correct=correct
        )
        append_csv(row)
        print(f"Run {i}: correct={correct}, t={runtime:.3f}s, mem={peak:.1f} KiB, FLOPs={flops}, E={per_run_energy} J")
