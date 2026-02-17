def isolate_blocks(lst):
    """
    Isolate items into blocks of three with single items in between.

    Args:
        lst: List of strings with length = n * 4 + 1 for some n

    Returns:
        List with alternating single items and groups of three items

    Raises:
        ValueError: If list length is invalid or items are not strings
    """
    # Check if list length matches the pattern: n * 4 + 1
    if (len(lst) - 1) % 4 != 0:
        raise ValueError("Invalid blocks")

    # Check if all items are strings
    if not all(isinstance(item, str) for item in lst):
        raise ValueError("Invalid items")

    # If list has only one item, return it as is
    if len(lst) == 1:
        return lst

    result = []
    i = 0

    while i < len(lst):
        # Add the single item
        result.append(lst[i])
        i += 1

        # If there are more items, add a group of three
        if i < len(lst):
            result.append([lst[i], lst[i + 1], lst[i + 2]])
            i += 3

    return result