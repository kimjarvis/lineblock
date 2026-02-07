# Lineblocks

Test code examples.

Linblocks is a tool for maintaining code documentation. Lineblocks keeps code documentation in sync with source code. 

It solves the issue of outdated documentation by:

- Storing examples in test source files (single source of truth).
- Preserving formatting during code insertion (unlike templating libraries such as jinja).
- Providing a CLI to automatically update documentation with the latest code.

# Installation 

```bash
pipx install lineblock
```
# Usage

## Ensure an example is tested

Add markers to the code that tests the example. 

```python
# examples/test_factorial.py
import pytest
# block extract examples/factorial_example.md
def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
# end extract
def test_factorial():
    assert factorial(5) == 120
```

Add markers to your documentation to indicate where the code example should be inserted.

```markdown
    A recursive function to calculate the factorial of a non-negative integer n.
    
    <!-- block insert examples/factorial_example.md 0 1 1 -->
    ```python
    ```
```

Extract the tested code example from source.

```bash
lineblock extract --source=examples/test_factorial.py
```

This generates a file `examples/factorial_example.md`.

```python
def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)
```

Insert the generated file into your documentation.

```bash
lineblock insert --source=examples/factorial.md
```

The example code is inserted into the documentation after the marker.  

```markdown
    <!-- block insert examples/factorial_example.md 0 1 1 -->
    ```python
    def factorial(n):
        if n == 0 or n == 1:
            return 1
        return n * factorial(n - 1)
    ```
    <!-- end insert -->
```

# About

Default marker formats are provided for Python and Markdown.

The Markdown insert begin marker is:

```
<!-- block insert examples/factorial_example.md 0 1 1 -->
```

The format of markers is:

```
prefix marker + filename + [optional indent] + [optional head] + [optional tail] + suffix marker
```

Where 
- *prefix marker* which, for Markdown sources, is `<!-- block insert`
- *filename* is the path to the file to insert
- *indent* is an optional number of spaces to indent the inserted code, defaults to 0, may be negative
- *head* is an optional number of lines to skip before inserting, defaults to 0 
- *tail* is an optional number of lines to skip after inserting, defaults to 0
- *suffix marker* which, for Markdown sources, is `-->`

## Indentation

Lineblocks controls block indentation.  The indentation of the marker is preserved, but can be modified by specifying an indent value on a marker.

## Head and Tail

Lineblocks can skip lines before and after the block.  This is useful when adding source code to documentation.  

Markers are comments, they should not appear in the rendered documentation.  However, many common documentation formats restrict the use of comments to 
certain sections.  In particular, they do not support comments in code blocks.  The solution is to create an empty code block in the documentation 
and add a marker before it.  The head and tail values can be used to insert the code into the correct place.

You can define custom markers for your source languages.  Markers are defined using regular expressions.  Custom markers can be specified using command parameters.    

## Lineblock module

Use the `lineblock` function to automate document generation.

**lineblock docstring**



