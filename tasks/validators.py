from importlib import import_module
import math, inspect, time

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

def _safe_eq_dict_lists(a, b):
    """Compare dict[str, list[str]] with order preserved within each list."""
    if not isinstance(a, dict) or not isinstance(b, dict):
        return False
    if set(a.keys()) != set(b.keys()):
        return False
    for k in a.keys():
        va, vb = a[k], b[k]
        if not isinstance(va, list) or not isinstance(vb, list):
            return False
        if va != vb:
            return False
    return True

def _sort_rows(rows):
    # Stable sort for list[dict] based on common keys used in json_data_normalizer
    return sorted(rows, key=lambda r: (r.get("record_id"), r.get("sku") or ""))

def validate(task_id: str, impl_module: str) -> bool:
    """
    Returns True iff the candidate implementation in `impl_module` passes
    task-specific correctness checks. Any exception or signature mismatch
    is treated as invalid (False), not a hard crash.
    """
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
        
        if task_id == "log_file_parser":
            # run_task is expected to accept a list[str] of log lines and return dict[str, list[str]]
            lines = [
                "[t] INFO start",
                "[t] ERROR E123: bad",
                "2025-01-01T00:00:00Z ERROR E123 repeated",
                "[t] WARN minor",
                "[t] ERROR E42: minor",
                "no level here",
                "2025-01-01T00:00:00Z ERROR E999 Disk full",
                "[t] ERROR : missing code",
            ]
            out = mod.run_task(lines)
            if not isinstance(out, dict):
                return False
            expected = {
                "E123": ["[t] ERROR E123: bad", "2025-01-01T00:00:00Z ERROR E123 repeated"],
                "E42":  ["[t] ERROR E42: minor"],
                "E999": ["2025-01-01T00:00:00Z ERROR E999 Disk full"],
            }
            # must not create spurious keys like "E" from "ERROR : ..."
            if "E" in out:
                return False
            return _safe_eq_dict_lists(out, expected)

        if task_id == "json_data_normalizer":
            # run_task expects a list[dict] and returns a flat list[dict] rows
            data = [
                {"id": 10, "timestamp": "t1", "user": {"id": 1, "name": "Ann"}, "items": [{"sku": "A", "qty": 2}]},
                {"id": 11, "timestamp": "t2", "items": [{"sku": "B", "qty": 1}, {"sku": "C", "qty": 5}]},
                {"id": 12, "timestamp": "t3", "user": {"id": 2, "name": "Bo"}, "items": []},
                {"id": 13, "timestamp": "t4"},  # no items
            ]
            out = mod.run_task(data)
            if not isinstance(out, list):
                return False
            want = [
                {"record_id":10,"timestamp":"t1","user_id":1,"user_name":"Ann","sku":"A","qty":2},
                {"record_id":11,"timestamp":"t2","user_id":None,"user_name":None,"sku":"B","qty":1},
                {"record_id":11,"timestamp":"t2","user_id":None,"user_name":None,"sku":"C","qty":5},
            ]
            try:
                # compare as sets with deterministic ordering
                return _sort_rows(out) == _sort_rows(want)
            except Exception:
                return False

        if task_id == "cache_with_expiry":
            """
            Expectation: run_task returns True when a basic TTL behavior test passes.
            We attempt a few calling conventions to be robust to signature differences:
              - run_task(ttl_seconds=1)
              - run_task(1)
              - run_task()   (where the function internally tests TTL behavior)
            Valid behavior:
              1) get("k") -> None
              2) put("k","v") then get("k") == "v"
              3) after ~1.1s, get("k") -> None (expired)
              4) put again and get returns the new value
            """
            # Preferred: let the candidate perform and return a boolean (self-test)
            # Try keyword first, then positional, then no-arg.
            try_orders = [
                lambda: mod.run_task(ttl_seconds=1),  # keyword
                lambda: mod.run_task(1),              # positional
                lambda: mod.run_task(),               # no-arg
            ]
            for attempt in try_orders:
                try:
                    res = attempt()
                    if isinstance(res, bool):
                        return res
                except TypeError:
                    # signature mismatch, try next calling convention
                    continue
            # If candidate didn't implement a self-test returning bool, we cannot validate further.
            # Treat as invalid.
            return False

    except TypeError:
        # wrong signature → treat as invalid, not a hard crash
        return False
    except Exception:
        # any runtime failure → invalid
        return False

    return False
