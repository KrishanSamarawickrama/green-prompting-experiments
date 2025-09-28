from tasks.reference.unit_test_gen_human import run_task

def test_unit_test_gen_reference():
    s = run_task()
    assert isinstance(s, str)
    assert "def test_" in s
