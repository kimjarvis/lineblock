import sys
import re
import yaml
from yaml.scanner import ScannerError
from yaml.parser import ParserError


def extract(line):
    """
    Extract text between {{ and }} if present in the line and validate if it's valid YAML.

    Args:
        line: A string line to process

    Returns:
        Dictionary with keys:
            found: Boolean indicating if {{...}} was found
            inside: The text between the braces (if found, otherwise empty string)
            yaml: Boolean indicating if the content is valid YAML (only if found=True)
            parameters: Python dictionary of parsed YAML (only if yaml=True)
    """
    # Pattern to match {{ ... }} with non-greedy matching
    pattern = r'\{\{(.*?)\}\}'
    match = re.search(pattern, line)

    result = {'found': False, 'inside': ''}

    if match:
        # Extract the text inside the braces and strip whitespace
        inside_text = match.group(1).strip()
        result = {'found': True, 'inside': inside_text}

        # Wrap the content in single braces for YAML validation
        yaml_content = f"{{{inside_text}}}"

        try:
            # Try to parse as YAML
            parsed_yaml = yaml.safe_load(yaml_content)
            # If we get here, it's valid YAML
            result['yaml'] = True
            result['parameters'] = parsed_yaml
        except (ScannerError, ParserError, yaml.YAMLError):
            # Not valid YAML
            result['yaml'] = False
            result['parameters'] = {}

    return result


def main():
    lines = """
line 1
line 2 
line 3 {{ source: "abc", to: "end" }}
line 4    
{{ inside B }}
line 6
line 7 {{ end: true }}
line 8
"""

    # Split the multiline string into individual lines
    # strip() removes the leading/trailing newlines from the multiline string
    line_list = lines.strip().split('\n')

    # Process each line
    for i, line in enumerate(line_list, 1):
        result = extract(line)
        print(f"Line {i}: '{line}'")
        print(f"  Result: {result}")
        if result['found']:
            print(f"  Found text: '{result['inside']}'")
            if result.get('yaml', False):
                print(f"  Valid YAML! Parsed parameters: {result['parameters']}")
            else:
                print(f"  Invalid YAML content")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())