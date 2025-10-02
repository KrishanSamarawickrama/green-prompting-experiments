def run_task(n=10000):
    """
    This function computes a helper transform f(i) = sqrt((i % 97)^2 + 1) - 1 for each i in the range from 0 to n-1.
    It returns the final accumulated float sum.
    
    Time complexity: O(n), as we perform a constant amount of work for each element in the sequence.
    Space complexity: O(1), as we only store a single floating point number, not dependent on the size of n.
    """
    import math  # We need this library to use sqrt function
    
    result = 0.0  # Initialize result
    for i in range(n):
        f_i = math.sqrt((i % 97)**2 + 1) - 1  # Compute helper transform
        result += f_i  # Accumulate result
    
    return result