import random

def run_task(n=2000, seed=42):
    """
    Return a sorted list of n random integers in [0, 10000], seeded.
    Deterministic: same (n, seed) => identical output values/order.
    No prints, no I/O, no network.
    
    Algorithm: Fisher-Yates shuffle followed by sorting
    Complexity: O(n log n) due to the sorting step
    """
    random.seed(seed)
    arr = [random.randint(0, 10000) for _ in range(n)]
    arr.sort()
    return arr