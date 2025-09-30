import math
def run_task(n=10000):
    """Compute a numeric transform and return its final accumulated float sum."""
    # Set seed for deterministic behavior
    import random
    random.seed(42)
    
    total = 0.0
    for i in range(n):
        f_i = math.sqrt((i % 97)**2 + 1) - 1
        total += f_i
        
    return total