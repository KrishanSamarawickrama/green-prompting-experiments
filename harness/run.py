import argparse, tracemalloc, time, subprocess, csv, sys, random
from pathlib import Path
from importlib import import_module

from tasks.validators import validate
from harness.utils import parse_perf_stderr, FLOPS_EVENT, latest_generated_module

DATA_FILE = Path("data/derived/runs.csv")
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

# --- Energy helpers (per-run) ---
import csv as _csv, subprocess as _sp

def measure_energy_perf_snippet(snippet: str):
    """
    Uses perf RAPL counter power/energy-pkg/ to estimate CPU package Joules
    for the provided one-liner Python snippet (executed in a child process).
    """
    cmd = [
        "perf","stat","-x",",","-e","power/energy-pkg/",
        sys.executable,"-c", snippet
    ]
    proc = _sp.run(cmd, capture_output=True, text=True)
    joules = None
    for line in proc.stderr.splitlines():
        if "power/energy-pkg/" in line:
            parts = [p.strip() for p in line.split(",")]
            if parts:
                try:
                    joules = float(parts[0].replace(",", ""))
                except Exception:
                    try:
                        joules = float(line.strip().split()[0].replace(",", ""))
                    except Exception:
                        joules = None
            break
    return joules

def per_run_energy_from_csv(path: str, idx: int):
    """
    Reads a CSV with at least a column 'energy_j' and returns row[idx].energy_j
    (idx is zero-based per *logged* run; warmups are not logged).
    """
    try:
        with open(path, newline="") as f:
            r = _csv.DictReader(f)
            rows = list(r)
        if 0 <= idx < len(rows):
            v = rows[idx].get("energy_j", "")
            return float(v) if v not in (None, "",) else None
    except Exception:
        return None
    return None

# --- Entrypoint resolution & workloads ---
def has_run_task(mod) -> bool:
    return hasattr(mod, "run_task") and callable(getattr(mod, "run_task"))

def get_runner_callable(task_id: str, mod):
    """
    Returns a zero-arg callable that executes the task workload in-process
    (used for timing + tracemalloc).
    """
    if has_run_task(mod):
        run_task = getattr(mod, "run_task")
        
        # Task-specific argument handling
        if task_id == "inefficient_sort":
            return lambda: run_task(300, seed=7)
        elif task_id == "json_data_normalizer":
            # Build test data for json_data_normalizer
            def _runner():
                rnd = random.Random(42)
                data = []
                for rid in range(2000):
                    rec = {"id": rid, "timestamp": f"t{rid}"}
                    if rid % 4 == 0:
                        rec["user"] = {"id": rid % 10, "name": f"U{rid%10}"}
                    # 0–3 items
                    k = rid % 3
                    if k:
                        rec["items"] = [{"sku": f"S{(rid+j)%50}", "qty": (j+1)} for j in range(k)]
                    data.append(rec)
                return run_task(data)
            return _runner
        elif task_id == "log_file_parser":
            # Build test log lines for log_file_parser
            def _runner():
                rnd = random.Random(42)
                lines = []
                for i in range(4000):
                    lines.append(f"[t] INFO start {i}")
                    if i % 3 == 0:
                        lines.append(f"[t] ERROR E123: bad {i}")
                    if i % 10 == 0:
                        lines.append(f"2025-01-01T00:00:00Z ERROR E42 minor {i}")
                    if i % 25 == 0 and rnd.random() < 0.5:
                        lines.append("unstructured line")
                return run_task(lines)
            return _runner
        else:
            # For other tasks, try calling with no arguments
            return run_task

    # Synthetic but stable workloads for developer tasks
    if task_id == "log_file_parser" and hasattr(mod, "parse_errors"):
        parse = getattr(mod, "parse_errors")
        def _runner():
            # Build ~10k lines with mixed levels; deterministic
            rnd = random.Random(42)
            lines = []
            for i in range(4000):
                lines.append(f"[t] INFO start {i}")
                if i % 3 == 0:
                    lines.append(f"[t] ERROR E123: bad {i}")
                if i % 10 == 0:
                    lines.append(f"2025-01-01T00:00:00Z ERROR E42 minor {i}")
                if i % 25 == 0 and rnd.random() < 0.5:
                    lines.append("unstructured line")
            _ = parse(lines)
        return _runner

    if task_id == "json_data_normalizer" and hasattr(mod, "normalize_records"):
        norm = getattr(mod, "normalize_records")
        def _runner():
            rnd = random.Random(42)
            data = []
            for rid in range(2000):
                rec = {"id": rid, "timestamp": f"t{rid}"}
                if rid % 4 == 0:
                    rec["user"] = {"id": rid % 10, "name": f"U{rid%10}"}
                # 0–3 items
                k = rid % 3
                if k:
                    rec["items"] = [{"sku": f"S{(rid+j)%50}", "qty": (j+1)} for j in range(k)]
                data.append(rec)
            _ = norm(data)
        return _runner

    if task_id == "cache_with_expiry" and hasattr(mod, "ExpiringCache"):
        Cache = getattr(mod, "ExpiringCache")
        def _runner():
            c = Cache(ttl_seconds=60)
            # exercise put/get; no sleeps (expiration not required during run)
            for i in range(20000):
                k = f"k{i%2000}"
                if i % 3 == 0:
                    c.put(k, str(i))
                _ = c.get(k)
        return _runner

    # Fallback: try common function names if present
    for name in ("main", "run", "solve"):
        if hasattr(mod, name) and callable(getattr(mod, name)):
            return getattr(mod, name)

    raise AttributeError(f"No runnable entrypoint found for task '{task_id}'. Module lacks run_task and known APIs.")

def get_runner_snippet(task_id: str, module_name: str) -> str:
    """
    Returns a Python snippet suitable for `python -c` that executes the same workload
    as get_runner_callable, so perf can measure counters/energy in a child process.
    """
    base = f"import importlib,random; m=importlib.import_module('{module_name}'); "
    if has_run_task(import_module(module_name)):
        if task_id == "inefficient_sort":
            return base + "m.run_task(300, seed=7)"
        elif task_id == "json_data_normalizer":
            return base + (
                "rnd=random.Random(42); "
                "data=[]; "
                "for rid in range(2000): "
                "  rec={'id':rid,'timestamp':f't{rid}'}; "
                "  "
                "  rec.update({'user':{'id':rid%10,'name':f'U{rid%10}'}}) if rid%4==0 else None; "
                "  k=rid%3; "
                "  rec.update({'items':[{'sku':f'S{(rid+j)%50}','qty':(j+1)} for j in range(k)]}) if k else None; "
                "  data.append(rec); "
                "m.run_task(data)"
            )
        elif task_id == "log_file_parser":
            return base + (
                "rnd=random.Random(42); "
                "lines=[]; "
                "import sys; "
                "[(lines.append(f'[t] INFO start {i}'), "
                "  lines.append(f'[t] ERROR E123: bad {i}') if i%3==0 else None, "
                "  lines.append(f'2025-01-01T00:00:00Z ERROR E42 minor {i}') if i%10==0 else None, "
                "  lines.append('unstructured line') if (i%25==0 and rnd.random()<0.5) else None) "
                " for i in range(4000)]; "
                "m.run_task(lines)"
            )
        else:
            # For other tasks, try calling with no arguments
            return base + "m.run_task()"

    if task_id == "log_file_parser":
        return base + (
            "parse=getattr(m,'parse_errors'); rnd=random.Random(42); "
            "lines=[]; "
            "import sys; "
            "[(lines.append(f'[t] INFO start {i}'), "
            "  lines.append(f'[t] ERROR E123: bad {i}') if i%3==0 else None, "
            "  lines.append(f'2025-01-01T00:00:00Z ERROR E42 minor {i}') if i%10==0 else None, "
            "  lines.append('unstructured line') if (i%25==0 and rnd.random()<0.5) else None) "
            " for i in range(4000)]; "
            "_=parse(lines)"
        )
    if task_id == "json_data_normalizer":
        return base + (
            "norm=getattr(m,'normalize_records'); rnd=random.Random(42); "
            "data=[]; "
            "for rid in range(2000): "
            "  rec={'id':rid,'timestamp':f't{rid}'}; "
            "  "
            "  rec.update({'user':{'id':rid%10,'name':f'U{rid%10}'}}) if rid%4==0 else None; "
            "  k=rid%3; "
            "  rec.update({'items':[{'sku':f'S{(rid+j)%50}','qty':(j+1)} for j in range(k)]}) if k else None; "
            "  data.append(rec); "
            "_=norm(data)"
        )
    if task_id == "cache_with_expiry":
        return base + (
            "Cache=getattr(m,'ExpiringCache'); c=Cache(ttl_seconds=60); "
            "from time import time; "
            "for i in range(20000): "
            "  k=f'k{i%2000}'; "
            "  (c.put(k,str(i)) if i%3==0 else None); "
            "  _=c.get(k)"
        )

    # Try common names
    return base + (
        "fn=None\n"
        "for name in ('run_task','main','run','solve'):\n"
        "  fn=getattr(m,name,None)\n"
        "  if callable(fn): break\n"
        "fn() if fn else (_ for _ in ()).throw(RuntimeError('no entrypoint'))"
    )

# --- Measurement helpers ---
def run_with_tracemalloc(runner):
    tracemalloc.start()
    t0 = time.perf_counter()
    runner()
    dt = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return dt, peak / 1024.0  # KiB (float)

def run_with_perf_snippet(snippet: str):
    cmd = [
        "perf", "stat", "-x", ",", "-e", FLOPS_EVENT,
        sys.executable, "-c", snippet
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
    ap.add_argument(
        "--task-id",
        required=True,
        choices=[
            # existing
            "inefficient_sort","modular_example","unit_test_gen",
            # new realistic developer tasks
            "log_file_parser","json_data_normalizer","cache_with_expiry",
        ],
    )
    ap.add_argument("--impl", required=True, help="Module path. Use tasks.generated.<task>.AUTO_PICK to select latest.")
    ap.add_argument("--variant", default="candidate")
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--warmup", type=int, default=2, help="Warm-up runs to discard")
    ap.add_argument("--energy-source", choices=["none","perf","csv"], default="none", help="How to capture per-run energy")
    ap.add_argument("--energy-csv", default="", help="CSV with per-run energy_j (when --energy-source=csv)")
    ap.add_argument("--skip-perf", action="store_true", help="Skip FLOPs measurement if perf missing.")
    args = ap.parse_args()

    print(f"[INFO] Starting run harness for task: {args.task_id}")
    impl = args.impl
    print(f"[INFO] Implementation module: {impl}")
    if impl.endswith(".AUTO_PICK"):
        print(f"[INFO] AUTO_PICK enabled. Locating latest generated module for task: {args.task_id}")
        mod_path = latest_generated_module(args.task_id)
        if not mod_path:
            print(f"[ERROR] No generated module found for task {args.task_id}.")
            raise SystemExit(f"No generated module found for task {args.task_id}.")
        print(f"[INFO] Latest generated module: {mod_path}")
        impl = mod_path

    print(f"[INFO] Loading module: {impl}")
    mod = import_module(impl)

    print(f"[INFO] Validating implementation...")
    correct = 1 if validate(args.task_id, impl) else 0
    print(f"[INFO] Validation result: {'correct' if correct else 'incorrect'}")

    # Resolve in-process runner and external snippet
    runner = get_runner_callable(args.task_id, mod)
    snippet = get_runner_snippet(args.task_id, mod.__name__)

    total_iters = args.warmup + args.runs
    print(f"[INFO] Total iterations: {total_iters} (warmup: {args.warmup}, runs: {args.runs})")
    for i in range(total_iters):
        print(f"[INFO] Iteration {i+1}/{total_iters}")
        print(f"[INFO] Running with tracemalloc...")
        runtime, peak = run_with_tracemalloc(runner)

        flops = None
        if not args.skip_perf:
            print(f"[INFO] Measuring FLOPs with perf (event={FLOPS_EVENT})...")
            try:
                flops = run_with_perf_snippet(snippet)
                print(f"[INFO] FLOPs measured: {flops}")
            except Exception as e:
                print(f"[WARN] FLOPs measurement failed: {e}")
                flops = None

        # Energy per run (program-under-test)
        if args.energy_source == "perf":
            print(f"[INFO] Measuring energy with perf...")
            try:
                energy_j = measure_energy_perf_snippet(snippet)
                print(f"[INFO] Energy measured: {energy_j} J")
            except Exception as e:
                print(f"[WARN] Energy measurement failed: {e}")
                energy_j = None
        elif args.energy_source == "csv":
            idx = i - args.warmup
            print(f"[INFO] Reading energy from CSV: {args.energy_csv}, index: {idx}")
            energy_j = per_run_energy_from_csv(args.energy_csv, idx)
            print(f"[INFO] Energy from CSV: {energy_j} J")
        else:
            energy_j = None

        if i < args.warmup:
            print(f"[INFO] Warm-up {i+1}: correct={correct}, t={runtime:.3f}s, mem={peak:.1f} KiB, FLOPs={flops}, E={energy_j}")
            continue

        row = dict(
            task_id=args.task_id, impl=impl, variant=args.variant, run_idx=i - args.warmup,
            runtime_s=runtime, mem_kib=peak, flops=flops if flops is not None else "",
            energy_j=energy_j if energy_j is not None else "",
            correct=correct
        )
        print(f"[INFO] Appending results to CSV: {DATA_FILE}")
        append_csv(row)
        print(f"[RESULT] Run {i - args.warmup}: correct={correct}, t={runtime:.3f}s, mem={peak:.1f} KiB, FLOPs={flops}, E={energy_j}")
