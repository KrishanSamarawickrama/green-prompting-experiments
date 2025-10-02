import math

def run_task(n=10000):
    """
    Iterates i from 0 to n-1, computes a helper transform f(i) = sqrt((i % 97)^2 + 1) - 1,
    and returns the final accumulated float sum.
    
    Time complexity: O(n)
    Space complexity: O(1)
    """
    total_sum = 0.0
    for i in range(n):
        mod_val = i % 97
        total_sum += math.sqrt(mod_val * mod_val + 1) - 1
    return total_sum