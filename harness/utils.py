import re, os, glob
FLOPS_EVENT = "fp_arith_inst_retired.scalar_double"

def parse_perf_stderr(stderr: str):
    """
    Extracts the FLOPs event count from perf stderr output.
    Looks for lines containing the event name and parses the first numeric column.
    Handles both regular format (whitespace-separated) and CSV format (comma-separated).
    """
    flops = None
    for line in stderr.splitlines():
        if FLOPS_EVENT in line:
            # Check if this is CSV format (contains commas)
            if "," in line:
                parts = line.strip().split(",")
            else:
                parts = line.strip().split()
            try:
                flops = int(parts[0].replace(",", ""))
            except Exception:
                pass
    return flops

def latest_generated_module(task_id: str):
    """
    Returns the module path (e.g., 'tasks.generated.inefficient_sort.file_123')
    of the most recent generated .py file for the task.
    """
    base = os.path.join("tasks", "generated", task_id)
    files = sorted(glob.glob(os.path.join(base, "*.py")), key=os.path.getmtime, reverse=True)
    if not files:
        return None
    path = files[0].replace(os.sep, ".")
    return path[:-3] if path.endswith(".py") else path
