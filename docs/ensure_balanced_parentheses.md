## Write a single function to perform the task.

Check in this order:

1. Check that the parentheses in the string are not nested.
  - Raise an a ValueError "Parentheses cannot be nested"
2. Check if the parentheses in the string are balanced.
  - Raise an a ValueError "Parentheses are not matched"

Function signature:

```python
def ensure_balanced_parentheses(string: str, open_parentheses: str="{{", close_parentheses: str="}}") -> None.
```

Check in this order:

1. open_parentheses and close_parentheses must be different.
  - Raise an a ValueError "Opening and closing parentheses must be different"
2. The last character of open_parentheses cannot be the same as the first character of close_parentheses.
    - Raise an a ValueError "The last character of open_parentheses cannot be the same as the first character of close_parentheses"

## Write pytest to verify the functionality.
Pytests should be in a separate file.

Minimum valid test cases:  

ensure_balanced_parentheses("")  
ensure_balanced_parentheses("{{ }}")

A ValueError shall be raised in these cases:

ensure_balanced_parentheses("{{ {{ }}")
ensure_balanced_parentheses("{{ {{ }} }}")