from importlib import import_module
import math, inspect

def _accepts_seed(fn):
    try:
        return "seed" in inspect.signature(fn).parameters
    except Exception:
        return False

def _as_list(x):
    # normalize numpy arrays and tuples to a Python list; reject others
    try:
        import numpy as _np
        if isinstance(x, _np.ndarray):
            return x.tolist()
    except Exception:
        pass
    if isinstance(x, (list, tuple)):
        return list(x)
    return None

def validate(task_id: str, impl_module: str) -> bool:
    mod = import_module(impl_module)
    if not hasattr(mod, "run_task"):
        return False

    try:
        if task_id == "inefficient_sort":
            # call with or without seed param
            out = mod.run_task(300, seed=7) if _accepts_seed(mod.run_task) else mod.run_task(300)
            lst = _as_list(out)
            if lst is None:
                return False
            # must be sorted and correct length
            return len(lst) == 300 and lst == sorted(lst)

        if task_id == "modular_example":
            out = mod.run_task(1000)
            return isinstance(out, float) and math.isfinite(out)

        if task_id == "unit_test_gen":
            s = mod.run_task()
            return isinstance(s, str) and "def test_" in s

    except TypeError:
        # wrong signature → treat as invalid, not a hard crash
        return False
    except Exception:
        # any runtime failure → invalid
        return False

    return False
