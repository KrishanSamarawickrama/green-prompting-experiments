from tasks.reference.inefficient_sort_human import run_task as sort_run
from tasks.reference.modular_example_human import run_task as mod_run

def test_sort_reference():
    out = sort_run(200, seed=1)
    assert out == sorted(out)

def test_mod_reference():
    out = mod_run(1000)
    assert isinstance(out, float)
