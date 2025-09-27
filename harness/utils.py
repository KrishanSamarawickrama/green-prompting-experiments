import re, os, glob
FLOPS_EVENT = "fp_arith_inst_retired.scalar_double"

def parse_perf_stderr(stderr: str):
    flops = None
    for line in stderr.splitlines():
        if FLOPS_EVENT in line:
            parts = line.strip().split()
            try:
                flops = int(parts[0].replace(",", ""))
            except Exception:
                pass
    return flops

def latest_generated_module(task_id: str):
    base = os.path.join("tasks","generated",task_id)
    files = sorted(glob.glob(os.path.join(base, "*.py")), key=os.path.getmtime, reverse=True)
    if not files:
        return None
    # convert path to module
    path = files[0].replace(os.sep, ".")
    if path.endswith(".py"):
        path = path[:-3]
    return path
