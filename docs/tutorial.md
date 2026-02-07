# Tutorial

## Ensure that doucmented examples are tested

It is very common for code documentation to contain examples that are not tested.

This is our markdown file fibonacci.md.
```markdown
    An iterative function to calculate the nth Fibonacci number.
    
    ```python
    def fibonacci(n):
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a
    ```
```

This is our test file test_fibonacci.py.

```python
import pytest

def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def test_fibonacci():
    assert fibonacci(10) == 55
```

The problem is that this test is a copy of the code example, not the code example itself.  The documenatation could be changed without updating the test or the test could be refactored without updating the documentation.   

## Test an example

We want to ensure that the code examples are tested when unit tests are run.

One solution to this problem is to copy the example from the documentation and add it to a test file as part of the build process.
To achieve this we need to add markers to the documentation to indicate where the code example should be extracted from.
We also add markers to the test file to indicate where the code example should be inserted.
We then run lineblock, using either the lineblock CLI or a function from the lineblock Python module, to extract the code example from the source file and insert it into the test file.

This is our markdown file fibonacci.md with markers added.
```markdown
    An iterative function to calculate the nth Fibonacci number.
    
    <!-- block extract examples/fibonacci.py 0 1 1 -->
    ```python
    def fibonacci(n):
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a
    ```
    <!-- end extract -->
```

The markers are markdown comments, they do not appear in the rendered documentation.  The block extract marker has four parameters.  The first is the path to the source file to be created.  The second parameter is 
the number of spaces to shift the code block to the right, it is zero here.  The third parameter is the number of lines to skip before starting to extract the code.  The forth is the number of lines between the end of the code block and the 
end extract marker.

Use the linebock CLI to extract the code block from the documentation.

```bash
lineblock extract --source=examples/fibonacci.md
```

This generates a file `examples/fibonacci.py`.

```python
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
```

Now we create a unit test for the code example in `examples/test_fibonacci.py`.

```python
    import pytest
    # block insert examples/fibonacci.py
    def test_fibonacci():
        assert fibonacci(10) == 55
```

Use the linebock CLI to insert the code block into the test.

```python
lineblock insert --source=examples/test_fibonacci.py
```

The unit test `examples/test_fibonacci.py` now contains the code block.

```python
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
```

If the test passes we can be confident that the example code in the documentation is correct.

## Create an example from a test

In our previous example the single source of truth was the code doucmentation.  The test was generated from the documentation.
In this example the single source of truth is a test. We will generate the documentation from a test.  This is preferable in many cases
because the test can be refactored, using an IDE or AI, without breaking the documentation.



