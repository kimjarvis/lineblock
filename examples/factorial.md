# Factorial

A recursive function to calculate the factorial of a non-negative integer n.

<!-- block insert examples/factorial_example.md 0 1 3-->
line 1
def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
line 2
line 3
line 4
<!-- end insert -->
