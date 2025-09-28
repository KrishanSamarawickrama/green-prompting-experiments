# Unit Test Generation

Write a `run_task()` function that **returns a string containing Python unit tests** for a simple target function.

**Important**: Do NOT write the unit tests directly. Instead, write a function that returns the test code as a string.

Target function (assumed given in the prompt):

```python
def add(a, b): return a + b
```

Expected output format:

```python
def run_task():
    return """import unittest
    
class TestAdd(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(add(2, 3), 5)
    
    def test_negative(self):
        self.assertEqual(add(-1, -4), -5)
        
    def test_edge_zero(self):
        self.assertEqual(add(0, 0), 0)

if __name__ == '__main__':
    unittest.main()
"""
```

Constraints:

- The `run_task()` function must return a string, not execute tests directly
- Tests must be unittest or pytest style
- At least 3 distinct cases (positive, negative, edge)
- Must run deterministically (no randomness)
- No network / file I/O
- The returned string must be valid Python code that can be executed