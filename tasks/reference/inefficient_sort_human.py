import random

def run_task(n=2000, seed=42):
    random.seed(seed)
    arr = [random.randint(0, 10000) for _ in range(n)]
    arr.sort()
    return arr
