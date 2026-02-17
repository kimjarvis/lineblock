# parentheses_checker.py

def ensure_balanced_parentheses(string: str, open_parentheses: str = "{{", close_parentheses: str = "}}") -> None:
    """
    Check that parentheses in a string are balanced and not nested.

    Args:
        string: The string to check
        open_parentheses: The opening parentheses string (default: "{{")
        close_parentheses: The closing parentheses string (default: "}}")

    Raises:
        ValueError: If validation fails with specific error messages
    """
    # Check if opening and closing parentheses are different
    if open_parentheses == close_parentheses:
        raise ValueError("Opening and closing parentheses must be different")

    # Check if the last character of open_parentheses equals the first character of close_parentheses
    if open_parentheses[-1] == close_parentheses[0]:
        raise ValueError(
            "The last character of open_parentheses cannot be the same as the first character of close_parentheses")

    open_len = len(open_parentheses)
    close_len = len(close_parentheses)

    i = 0
    found_open = False

    while i < len(string):
        # Check for opening parentheses
        if string[i:i + open_len] == open_parentheses:
            if found_open:
                raise ValueError("Parentheses cannot be nested")
            found_open = True
            i += open_len

        # Check for closing parentheses
        elif string[i:i + close_len] == close_parentheses:
            if not found_open:
                raise ValueError("Parentheses are not matched")
            found_open = False
            i += close_len
        else:
            i += 1

    # Check if there's an unclosed opening parenthesis
    if found_open:
        raise ValueError("Parentheses are not matched")