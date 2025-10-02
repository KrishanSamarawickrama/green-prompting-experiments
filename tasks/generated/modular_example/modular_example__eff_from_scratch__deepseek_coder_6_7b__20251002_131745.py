import math

def run_task(n=10000):
    """
    This function computes a helper transform for each i in range 0..n-1, and returns the final accumulated float sum.
    
    The complexity of this algorithm is O(n), as it iterates over n elements exactly once.
    """
    return sum((math.sqrt((i % 97) ** 2 + 1) - 1) for i in range(n))