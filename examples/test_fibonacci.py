# examples/test_fibonacci.py
import pytest
# block insert examples/fibonacci.py
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
# end insert
def test_fibonacci():
    assert fibonacci(10) == 55
