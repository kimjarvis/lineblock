# Lineblocks

Linblocks is a tool for maintaining code documentation. It keeps code documentation in sync with source code. 

It solves the issue of outdated documentation by:

- Storing code examples in source files (single source of truth)
- Preserving formatting during code insertion (unlike templating libraries such as jinja)
- Automatically updating documentation with the latest code

# Installation 

```bash
pipx install lineblock
```
# Usage

Add markers to the code that tests your example. 

```python
# examples/test_factorial.py
import pytest
# block extract examples/factorial_example.md ```python
def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
# end extract ```
def test_factorial():
    assert factorial(5) == 120
```

Add markers to your documentation to indicate where the code example should be inserted.

```markdown
    <!-- block insert examples/factorial_example.md -->
```

Extract the tested code example from source.

```bash
lineblock extract --source=examples/test_factorial.py
```

Insert the example into your documentation.

```bash
lineblock insert --source=examples/factorial.md
```

The example code is inserted into the documentation after the marker.  
The marker is a comment, it will not appear in the rendered documentation.
The markdown prefix ````python` and suffix, specified on the extract marker, wrap the code block. 

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

Lineblocks gives you control over block indentation.  Indentation is preserved but can be modified by specifying a value on a marker.
 
You can define custom markers for your source languages.  Markers are defined using regular expressions.  Custom markers can be specified using command parameters.    
Default markers are provided for many common source types. 
See documentation for details.

Use the `lineblock` function to automate document generation.






