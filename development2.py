
q="""
Write a single function to perform the task.
Raise an a ValueError "Parentheses are not matched"

Function signature:

```python
def ensure_balanced_parentheses(string: str, open_parentheses: str="{{", close_parentheses: str="}}") -> None.
```

## Write pytest to verify the functionality.

Minimum valid test cases:

ensure_balanced_parentheses("")
ensure_balanced_parentheses("{{ }}")

A ValueError shall be raised in this cases

ensure_balanced_parentheses("{{ {{ }}")
"""


def ensure_balanced_parentheses(string: str, open_parentheses: str = "{{", close_parentheses: str = "}}") -> None:
    """
    Ensure that the parentheses in the string are balanced.

    Args:
        string: The string to check for balanced parentheses
        open_parentheses: The opening parentheses string (default: "{{")
        close_parentheses: The closing parentheses string (default: "}}")

    Raises:
        ValueError: If the parentheses are not matched
    """
    stack = []
    i = 0

    while i < len(string):
        # Check for opening parentheses
        if string[i:i + len(open_parentheses)] == open_parentheses:
            stack.append(open_parentheses)
            i += len(open_parentheses)
        # Check for closing parentheses
        elif string[i:i + len(close_parentheses)] == close_parentheses:
            if not stack or stack.pop() != open_parentheses:
                raise ValueError("Parentheses are not matched")
            i += len(close_parentheses)
        else:
            i += 1

    # If there's anything left in the stack, parentheses are not matched
    if stack:
        raise ValueError("Parentheses are not matched")


# test_balanced_parentheses.py
import pytest
from src import ensure_balanced_parentheses


def test_empty_string():
    """Test that empty string passes validation"""
    ensure_balanced_parentheses("")

def test_simple_balanced_parentheses():
    """Test simple balanced parentheses with spaces"""
    ensure_balanced_parentheses("{{ }}")

def test_nested_balanced_parentheses():
    """Test nested balanced parentheses"""
    ensure_balanced_parentheses("{{ {{ }} }}")

def test_balanced_with_text():
    """Test balanced parentheses with surrounding text"""
    ensure_balanced_parentheses("text {{ content }} more text")

def test_multiple_balanced_pairs():
    """Test multiple balanced parentheses pairs"""
    ensure_balanced_parentheses("{{ first }} and {{ second }}")

def test_custom_parentheses():
    """Test with custom parentheses symbols"""
    ensure_balanced_parentheses("<tag>content</tag>", "<tag>", "</tag>")

def test_unmatched_opening_raises_error():
    """Test that unmatched opening parentheses raise ValueError"""
    with pytest.raises(ValueError, match="Parentheses are not matched"):
        ensure_balanced_parentheses("{{ {{ }}")

def test_unmatched_closing_raises_error():
    """Test that unmatched closing parentheses raise ValueError"""
    with pytest.raises(ValueError, match="Parentheses are not matched"):
        ensure_balanced_parentheses("{{ }} }}")

def test_wrong_order_raises_error():
    """Test that wrong order of parentheses raises ValueError"""
    with pytest.raises(ValueError, match="Parentheses are not matched"):
        ensure_balanced_parentheses("}} {{")

def test_only_opening_raises_error():
    """Test that only opening parentheses raise ValueError"""
    with pytest.raises(ValueError, match="Parentheses are not matched"):
        ensure_balanced_parentheses("{{ {{")

def test_only_closing_raises_error():
    """Test that only closing parentheses raise ValueError"""
    with pytest.raises(ValueError, match="Parentheses are not matched"):
        ensure_balanced_parentheses("}} }}")