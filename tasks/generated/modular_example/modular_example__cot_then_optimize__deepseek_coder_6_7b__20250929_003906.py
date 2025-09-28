def run_task(n=10000):
    total = 0.0
    for i in range(n):
        f = ((i % 97) ** 2 + 1) - 1
        total += f
    return total