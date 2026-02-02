# Lineblocks

Lineblocks is a tool that keeps code documentation in sync with source code.

Primary Use Case: Maintaining Code Documentation

It solves the issue of outdated documentation by:

- Storing code examples in source files (single source of truth)
- Automatically updating documentation with latest code
- Preserving formatting during code insertion
- Detecting errors like missing files or markers

# Installation 

```bash
pipx install lineblock
```
# Usage

Add markers to the code that tests your example. 

```python
# examples/test_factorial.py
import pytest
# block extract examples/factorial_example.md 4 ```python
def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
# end extract ```
def test_factorial():
    assert factorial(5) == 120
```

Add markers to your documentation to indicate where code example should be inserted.

```
<!-- block insert factorial.md -->
```

Extract the tested code example from source.

```bash
lineblock extract --source=examples/test_factorial.py
```

Insert the example into your documentation.

```bash
lineblock insert --source=examples/factorial.md
```

Documentaton with the code example inserted

```markdown
    <!-- block insert examples/factorial_example.md -->
    ```python
        def factorial(n):
            if n == 0 or n == 1:
                return 1
            return n * factorial(n - 1)
    ```
    <!-- end insert -->
```

Use the `lineblock` function to automate document generation.






