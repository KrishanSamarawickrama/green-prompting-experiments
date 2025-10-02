import math

def run_task(n=10000):
    total_sum = 0.0
    for i in range(n):
        transform = math.sqrt((i % 97) ** 2 + 1) - 1
        total_sum += transform
    return total_sum