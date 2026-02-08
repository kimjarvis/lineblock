# Fibonacci

An iterative function to calculate the nth Fibonacci number.

<!-- block extract "fibonacci example" 0 1 1 -->
```python
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
```
<!-- end extract -->
