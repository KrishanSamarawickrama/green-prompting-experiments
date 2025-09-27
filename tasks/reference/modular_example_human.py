import math

def helper_transform(x):
    return math.sqrt(x*x + 1) - 1

def run_task(n=10000):
    s = 0.0
    for i in range(n):
        s += helper_transform(i % 97)
    return s
