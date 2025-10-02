import random

def run_task(n=2000, seed=42):
    """
    Return a sorted list of n random integers in  [0, 10000], seeded.
    Deterministic: same (n, seed) => identical output values/order.
    No prints, no I/O, no network.
    """
    # Seed RNG with seed.
    random.seed(seed)
    
    # Generate list of length n with values in [0, 10000].
    nums = [random.randint(0, 10000) for _ in range(n)]
    
    # Sort in non-decreasing order and return the sorted list.
    return sorted(nums)