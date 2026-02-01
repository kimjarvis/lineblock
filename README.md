# Lineblocks

Lineblocks is a documentation synchronization tool that maintains consistency between code examples and their corresponding documentation.

Primary Use Case: Keeping Code Documentation Up to Date

The tool addresses the common problem where documentation becomes outdated as code evolves. Developers often copy-paste code examples into documentation, but when the source code changes, these examples quickly become inaccurate. This program solves this by:

- Single Source of Truth: Code examples are stored in actual source files, not duplicated in documentation

- Automatic Synchronization: Running this program updates all documentation with the latest code examples

- Consistent Formatting: Maintains proper indentation and structure when inserting code blocks

- Error Detection: Identifies orphaned markers and missing files to prevent broken documentation

# Installation 

```bash
pipx install lineblock
```
# Usage

Add markers to the source code

```python
import pytest
# block extract factorial.md 4 ```python
def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
# end extract ```
def test_factorial():
    assert factorial(5) == 120
```

Add markers to indicate where code examples should be inserted.

```
<!-- block insert factorial.md -->
```

Run the extraction process to extract code examples from your source code.

```bash
lineblock extract --source=test_factorial.py --prefix=.
```

Run the insertion process to insert code examples into your documentation.

```bash
lineblock insert --source=factorial.md --prefix=.
```


