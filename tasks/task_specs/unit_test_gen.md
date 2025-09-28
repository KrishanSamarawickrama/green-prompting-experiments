# Unit Test Generation

Write `run_task()` that **returns a string of Python unit tests** for a simple target function.

Target function (assumed given in the prompt):
```python
def add(a, b): return a + b
```

Constraints:
- Tests must be unittest or pytest style.
- At least 3 distinct cases (positive, negative, edge).
- Must run deterministically (no randomness).
- No network / file I/O.