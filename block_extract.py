#!/usr/bin/env python3

import argparse
import re
from pathlib import Path


class UnclosedBlockError(Exception):
    """Exception raised when a block extract marker is found without a corresponding end marker."""

    def __init__(self, source_file, line_number, line_content=""):
        self.source_file = source_file
        self.line_number = line_number
        self.line_content = line_content
        message = (f"Unclosed block starting at line {line_number} "
                   f"in file '{source_file}'. "
                   f"Expected end marker '# block end' or '<!-- block end -->'.")
        super().__init__(message)


class OrphanedEndMarkerError(Exception):
    """Exception raised when a block end marker is found without a corresponding start marker."""

    def __init__(self, source_file, line_number, line_content=""):
        self.source_file = source_file
        self.line_number = line_number
        self.line_content = line_content
        message = (f"Orphaned block end marker at line {line_number} "
                   f"in file '{source_file}'. "
                   f"No corresponding '# block extract' or '<!-- block extract -->' marker found.")
        super().__init__(message)


def is_start_marker(line):
    s = line.strip()
    if re.fullmatch(r"#\s*block extract\s+\S+.*", s):
        return True
    if re.fullmatch(r"<!--\s*block extract\s+\S+.*-->", s):
        return True
    return False


def is_end_marker(line):
    s = line.strip()
    if re.fullmatch(r"#\s*block end\s*", s):
        return True
    if re.fullmatch(r"<!--\s*block end\s*-->", s):
        return True
    return False


def indent_lines(lines, spaces):
    indented = []
    for line in lines:
        stripped = line.rstrip("\n")
        if spaces >= 0:
            # Positive indent: add spaces
            indented_line = f"{' ' * spaces}{stripped}\n"
        else:
            # Negative indent: remove spaces from the beginning
            # Remove up to |spaces| spaces, but not beyond the first non-space character
            spaces_to_remove = -spaces
            # Count leading spaces in the original line
            leading_spaces = len(stripped) - len(stripped.lstrip())
            # Remove spaces, but not more than what exists
            remove_count = min(spaces_to_remove, leading_spaces)
            indented_line = stripped[remove_count:] + "\n"
        indented.append(indented_line)
    return indented


def extract_block_info(marker_line, extract_path):
    match = re.match(r"(\s*)#\s*block extract\s+(\S+)(?:\s+(-?\d+))?", marker_line)
    if match:
        leading_ws = match.group(1)
        file_name = match.group(2)
        extra_indent = int(match.group(3)) if match.group(3) else 0
        original_indent = len(leading_ws)
        total_indent = original_indent + extra_indent
        file_path = Path(extract_path) / file_name
        return file_path, total_indent

    match = re.match(r"(\s*)<!--\s*block extract\s+(\S+)(?:\s+(-?\d+))?\s*-->", marker_line)
    if match:
        leading_ws = match.group(1)
        file_name = match.group(2)
        extra_indent = int(match.group(3)) if match.group(3) else 0
        original_indent = len(leading_ws)
        total_indent = original_indent + extra_indent
        file_path = Path(extract_path) / file_name
        return file_path, total_indent

    return None


def process_file(source_file, extract_path):
    try:
        with open(source_file, "r") as f:
            original_lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Source file '{source_file}' not found.")
        return

    i = 0
    in_block = False  # Track if we're currently processing a block
    while i < len(original_lines):
        line = original_lines[i]

        if is_end_marker(line):
            # Check if we have an orphaned end marker
            if not in_block:
                raise OrphanedEndMarkerError(source_file, i + 1, line.strip())
            else:
                # Found the end of the current block
                in_block = False
                i += 1
                continue

        if is_start_marker(line):
            # Check if we're already in a block (nested blocks are not allowed)
            if in_block:
                # We're trying to start a new block while already in one
                raise OrphanedEndMarkerError(source_file, i + 1,
                                             "Found block extract marker without closing previous block.")

            info = extract_block_info(line, extract_path)
            if info:
                file_path, total_indent = info
                start_line = i + 1  # 1-based line number for error reporting
                i += 1
                block_lines = []
                in_block = True  # Now we're inside a block

                # Collect lines until we find the corresponding end marker
                while i < len(original_lines):
                    current_line = original_lines[i]
                    if is_end_marker(current_line):
                        # Found the end marker for this block
                        in_block = False
                        break
                    block_lines.append(current_line)
                    i += 1
                else:
                    # Reached end of file without finding end marker
                    raise UnclosedBlockError(source_file, start_line, line.strip())

                # Check if parent directories exist (don't create them)
                if not file_path.parent.exists():
                    raise ValueError(f"Parent directory does not exist for output file: '{file_path}'")

                # Write extracted block with indentation
                indented_lines = indent_lines(block_lines, total_indent)
                with open(file_path, "w") as out_f:
                    out_f.writelines(indented_lines)
        i += 1


def process_path(path, extract_path):
    path = Path(path).expanduser().resolve()
    extract_path = Path(extract_path).expanduser().resolve()

    # Raise FileNotFoundError if the source path doesn't exist
    if not path.exists():
        raise FileNotFoundError(f"Error: Source path '{path}' does not exist.")

    # Raise FileNotFoundError if the extract directory doesn't exist
    if not extract_path.exists():
        raise FileNotFoundError(f"Error: Extract path '{extract_path}' does not exist.")

    # Raise an error if extract_path exists but is not a directory
    if not extract_path.is_dir():
        raise NotADirectoryError(f"Error: Extract path '{extract_path}' is not a directory.")

    if path.is_file():
        process_file(path, extract_path)
    else:
        for file in path.rglob("*.py"):
            process_file(file, extract_path)


def block_extract(source_path, extract_path):
    try:
        process_path(source_path, extract_path)
    except (UnclosedBlockError, OrphanedEndMarkerError) as e:
        print(f"Error: {e}")
        raise  # Re-raise to exit with non-zero status
    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        print(f"Error: {e}")
        raise  # Re-raise to exit with non-zero status
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_path", required=True, help="Source file or directory.")
    parser.add_argument("--extract_path", required=True, help="Base path for block files.")
    args = parser.parse_args()

    try:
        block_extract(source_path=args.source_path, extract_path=args.extract_path)
    except (UnclosedBlockError, OrphanedEndMarkerError, FileNotFoundError, NotADirectoryError, ValueError):
        # Exit with non-zero status to indicate error
        exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        exit(1)


if __name__ == "__main__":
    main()