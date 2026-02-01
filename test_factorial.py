import pytest
# block extract factorial_example.md 4 ```python
def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
# end extract ```
def test_factorial():
    assert factorial(5) == 120
