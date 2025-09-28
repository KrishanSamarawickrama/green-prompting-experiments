def run_task():
    # Return a string of Python unit tests for add(a, b)
    return """import pytest

def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, -4) == -5

def test_add_zero():
    assert add(0, 0) == 0
"""