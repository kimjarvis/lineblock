import json


def process_chunks(x: list) -> list:
    """
    Process a list where items can be strings or sub-lists.

    For sub-lists with 3 string elements, parse the first and third elements as JSON
    and replace them with the resulting dictionaries.

    Args:
        x: A list containing strings and/or sub-lists

    Returns:
        A list with processed items

    Raises:
        ValueError: If validation fails or JSON parsing fails
    """
    result = []

    for item in x:
        # Check if item is a string - pass through unchanged
        if isinstance(item, str):
            result.append(item)
            continue

        # Check if item is a list
        if isinstance(item, list):
            # Check 1: Validate sub-list length is 3
            if len(item) != 3:
                raise ValueError("Invalid sub-list length")

            # Check 3: Validate all items in sub-list are strings
            for sub_item in item:
                if not isinstance(sub_item, str):
                    raise ValueError("Invalid list item")

            # Parse first and third items as JSON
            try:
                first_dict = json.loads(item[0])
            except json.JSONDecodeError:
                raise ValueError("Failed to parse JSON")

            try:
                third_dict = json.loads(item[2])
            except json.JSONDecodeError:
                raise ValueError("Failed to parse JSON")

            # Replace first and third items with parsed dictionaries
            processed_sublist = [first_dict, item[1], third_dict]
            result.append(processed_sublist)
            continue

        # Check 2: Item is neither string nor list
        raise ValueError("Invalid item type")

    return result