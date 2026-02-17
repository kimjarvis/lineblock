def parse_parentheses(string: str, open_parentheses: str = "{{", close_parentheses: str = "}}") -> list:
    """
    Parse a string by splitting at each pair of parentheses.

    Args:
        string: The input string to parse
        open_parentheses: The opening parenthesis delimiter
        close_parentheses: The closing parenthesis delimiter

    Returns:
        A list containing the text between each pair of parentheses,
        including empty strings where appropriate
    """
    result = []
    current_pos = 0
    len_open = len(open_parentheses)
    len_close = len(close_parentheses)

    # If there are no parentheses in the string, return the string as a single element
    if open_parentheses not in string and close_parentheses not in string:
        return [string]

    while current_pos < len(string):
        # Find the next opening parenthesis
        open_pos = string.find(open_parentheses, current_pos)

        if open_pos == -1:
            # No more opening parentheses, add remaining text and break
            result.append(string[current_pos:])
            break

        # Add text before the opening parenthesis
        result.append(string[current_pos:open_pos])

        # Find the closing parenthesis for this opening
        close_pos = string.find(close_parentheses, open_pos + len_open)

        # Extract text between parentheses
        between_text = string[open_pos + len_open:close_pos]
        result.append(between_text)

        # Move current position past the closing parenthesis
        current_pos = close_pos + len_close

    # If we've processed everything and there's no text after the last closing parenthesis,
    # we need to add an empty string for the trailing text
    if current_pos == len(string):
        result.append("")

    return result