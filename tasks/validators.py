from importlib import import_module
import math, random

def validate(task_id: str, impl_module: str) -> bool:
    mod = import_module(impl_module)
    if not hasattr(mod, "run_task"):
        return False

    if task_id == "inefficient_sort":
        res = mod.run_task(300, seed=7) if _accepts_seed(mod.run_task) else mod.run_task(300)
        return res == sorted(res)

    if task_id == "modular_example":
        out = mod.run_task(1000)
        return isinstance(out, float) and math.isfinite(out)
    
    if task_id == "unit_test_gen":
        out = mod.run_task()
        return isinstance(out, str) and "def test_" in out

    # Unknown task => pessimistic
    return False

def _accepts_seed(fn):
    try:
        import inspect
        return "seed" in inspect.signature(fn).parameters
    except Exception:
        return False
