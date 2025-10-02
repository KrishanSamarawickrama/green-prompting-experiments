import numpy as np

def run_task(n=2000, seed=42):
    """
    Return a sorted list of n random integers in [0, 10000], seeded.
    Deterministic: same (n, seed) => identical output values/order.
    No prints, no I/O, no network.
    """
    np.random.seed(seed)
    arr = np.random.randint(0, 10001, n)
    return np.sort(arr).tolist()