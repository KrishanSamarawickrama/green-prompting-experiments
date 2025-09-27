# Task: Modular Numeric Transform

Write a function `run_task(n=10000)` that:
- Iterates i from 0..n-1
- For each i, computes a helper transform f(i) = sqrt((i % 97)^2 + 1) - 1
- Returns the final accumulated float sum

Deterministic behavior required.
