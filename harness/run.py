import argparse, tracemalloc, time, subprocess, csv, sys
from pathlib import Path
from importlib import import_module

from tasks.validators import validate
from harness.utils import parse_perf_stderr, FLOPS_EVENT, latest_generated_module

DATA_FILE = Path("data/derived/runs.csv")
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

# --- Energy helpers (per-run) ---
import csv as _csv, subprocess as _sp

def measure_energy_perf(python_module_name: str):
    """
    Uses perf RAPL counter power/energy-pkg/ to estimate CPU package Joules
    for the program-under-test run.
    """
    cmd = [
        "perf","stat","-e","power/energy-pkg/",
        sys.executable,"-c",f"import importlib; m=importlib.import_module('{python_module_name}'); m.run_task()"
    ]
    proc = _sp.run(cmd, capture_output=True, text=True)
    joules = None
    for line in proc.stderr.splitlines():
        if "power/energy-pkg/" in line:
            parts = line.strip().split()
            try:
                joules = float(parts[0].replace(",", ""))
            except Exception:
                pass
    return joules

def per_run_energy_from_csv(path: str, idx: int):
    """
    Reads a CSV with at least a column 'energy_j' and returns row[idx].energy_j
    (idx is zero-based per *logged* run; warmups are not logged).
    """
    with open(path, newline="") as f:
        r = _csv.DictReader(f)
        rows = list(r)
    if idx < len(rows):
        try:
            return float(rows[idx].get("energy_j", ""))
        except Exception:
            return None
    return None

# --- Measurement helpers ---
def load_module(module_path: str):
    return import_module(module_path)

def run_with_tracemalloc(mod):
    tracemalloc.start()
    t0 = time.perf_counter()
    _ = mod.run_task()
    dt = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return dt, peak / 1024  # KiB

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
    ap.add_argument("--task-id", required=True, choices=["inefficient_sort","modular_example", "unit_test_gen"])
    ap.add_argument("--impl", required=True, help="Module path. Use tasks.generated.<task>.AUTO_PICK to select latest.")
    ap.add_argument("--variant", default="candidate")
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--warmup", type=int, default=2, help="Warm-up runs to discard")
    ap.add_argument("--energy-source", choices=["none","perf","csv"], default="none", help="How to capture per-run energy")
    ap.add_argument("--energy-csv", default="", help="CSV with per-run energy_j (when --energy-source=csv)")
    ap.add_argument("--skip-perf", action="store_true", help="Skip FLOPs measurement if perf missing.")
    args = ap.parse_args()

    impl = args.impl
    if impl.endswith(".AUTO_PICK"):
        mod_path = latest_generated_module(args.task_id)
        if not mod_path:
            raise SystemExit(f"No generated module found for task {args.task_id}.")
        impl = mod_path

    mod = load_module(impl)
    correct = 1 if validate(args.task_id, impl) else 0

    total_iters = args.warmup + args.runs
    for i in range(total_iters):
        runtime, peak = run_with_tracemalloc(mod)

        flops = None
        if not args.skip_perf:
            try:
                flops = run_with_perf(mod)
            except Exception:
                flops = None

        # Energy per run (program-under-test)
        if args.energy_source == "perf":
            energy_j = measure_energy_perf(mod.__name__)
        elif args.energy_source == "csv":
            energy_j = per_run_energy_from_csv(args.energy_csv, i - args.warmup)
        else:
            energy_j = None

        if i < args.warmup:
            print(f"Warm-up {i}: correct={correct}, t={runtime:.3f}s, mem={peak:.1f} KiB, FLOPs={flops}, E={energy_j}")
            continue

        row = dict(
            task_id=args.task_id, impl=impl, variant=args.variant, run_idx=i - args.warmup,
            runtime_s=runtime, mem_kib=peak, flops=flops if flops is not None else "",
            energy_j=energy_j if energy_j is not None else "",
            correct=correct
        )
        append_csv(row)
        print(f"Run {i - args.warmup}: correct={correct}, t={runtime:.3f}s, mem={peak:.1f} KiB, FLOPs={flops}, E={energy_j}")
