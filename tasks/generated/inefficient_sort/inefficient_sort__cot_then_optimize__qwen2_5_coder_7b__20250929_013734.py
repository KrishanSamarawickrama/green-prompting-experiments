import random

def run_task(n=2000, seed=42):
    """
    Return a sorted list of n random integers in [0, 10000], seeded.
    Deterministic: same (n, seed) => identical output values/order.
    No prints, no I/O, no network.
    """
    random.seed(seed)
    return sorted(random.randint(0, 10000) for _ in range(n))