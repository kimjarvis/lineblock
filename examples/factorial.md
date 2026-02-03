# Factorial

A recursive function to calculate the factorial of a non-negative integer n.

<!-- block insert examples/factorial_example.md -->
```python
def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
```
<!-- end insert -->
