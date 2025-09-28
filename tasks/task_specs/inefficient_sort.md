# Task: Inefficient Sort → Correct Sorted Output

You MUST implement EXACTLY this function signature and semantics:

```python
def run_task(n=2000, seed=42):
    """
    Return a sorted list of n random integers in [0, 10000], seeded.
    Deterministic: same (n, seed) => identical output values/order.
    No prints, no I/O, no network.
    """
 ```

Steps:

- Seed RNG with seed.
- Generate list of length n with values in [0, 10000].
- Sort in non-decreasing order and return the sorted list.
