# process_chunks.py
import json

def process_chunks(x: list[str]) -> list[str]:
    result = []
    for item in x:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, list):
            for sub_item in item:
                if not isinstance(sub_item, str):
                    raise ValueError("Invalid list item")
            if len(item) != 3:
                raise ValueError("Invalid sub-list length")
            try:
                first_parsed = json.loads(item[0])
                third_parsed = json.loads(item[2])
            except (json.JSONDecodeError, Exception):
                raise ValueError("Failed to parse JSON")
            result.append([first_parsed, item[1], third_parsed])
        else:
            raise ValueError("Invalid item type")
    return result