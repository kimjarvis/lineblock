import argparse
import re
from pathlib import Path


def indent_lines(lines, spaces):
    indented = []
    for line in lines:
        stripped = line.rstrip("\n")
        indented_line = f"{' ' * max(0, spaces)}{stripped}\n"
        indented.append(indented_line)
    return indented


def extract_block_info(marker_line, insert_path):
    # Match Python-style marker (# block insert ...)
    match = re.match(r"(\s*)#\s*block insert\s+(\S+)(?:\s+(-?\d+))?", marker_line)
    if not match:
        # Match Markdown-style marker (<!-- block insert ... -->)
        match = re.match(r"(\s*)<!--\s*block insert\s+(\S+)(?:\s+(-?\d+))?\s*-->", marker_line)
        if not match:
            return None

    leading_ws = match.group(1)
    file_name = match.group(2)
    extra_indent = int(match.group(3)) if match.group(3) else 0
    original_indent = len(leading_ws)
    total_indent = original_indent + extra_indent
    file_path = Path(insert_path) / file_name
    return file_path, total_indent, original_indent


def is_start_marker(line):
    line = line.strip()
    # Check for Python-style marker (# block insert ...)
    if re.fullmatch(r"\s*#\s*block insert\s+\S+.*", line):
        return True, "python"
    # Check for Markdown-style marker (<!-- block insert ... -->)
    if re.fullmatch(r"\s*<!--\s*block insert\s+\S+.*-->", line):
        return True, "markdown"
    return False


def is_end_marker(line):
    line = line.strip()
    # Check for Python-style marker (# block end)
    if re.fullmatch(r"\s*#\s*block end\s*", line):
        return True
    # Check for Markdown-style marker (<!-- block end -->)
    if re.fullmatch(r"\s*<!--\s*block end\s*-->", line):
        return True
    return False


def process_file(source_file, insert_path, clear_mode=False, remove_mode=False):
    try:
        with open(source_file, "r") as f:
            original_lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Source file '{source_file}' not found.")
        return

    output = []
    i = 0
    changed = False
    block_type = "none"  # Default block type

    while i < len(original_lines):
        line = original_lines[i]
        info = extract_block_info(line, insert_path)

        if info:
            file_path, total_indent, orig_indent = info

            # Find end marker
            end_i = None
            for j in range(i + 1, len(original_lines)):
                if is_end_marker(original_lines[j]):
                    end_i = j
                    break

            next_i = (end_i + 1) if end_i is not None else (i + 1)

            if clear_mode or remove_mode:
                # Keep only the start marker; drop content and end marker
                output.append(line)
                changed = True
            else:
                # Normal mode: insert content between markers
                replacement = [line]  # keep start marker

                # Read and insert block content
                block_content = []
                try:
                    with open(file_path, "r") as f:
                        block_content = f.readlines()
                    indented_block = indent_lines(block_content, total_indent)
                    replacement.extend(indented_block)
                except FileNotFoundError:
                    print(f"Warning: Block file '{file_path}' not found.")

                # Add end marker
                if block_type == "python":
                    replacement.append(f"{' ' * orig_indent}# block end\n")
                elif block_type == "markdown":
                    replacement.append(f"{' ' * orig_indent}<!-- block end -->\n")
                else:
                    replacement.append(f"{' ' * orig_indent}# block end\n")
                output.extend(replacement)
                changed = True

            i = next_i
        else:
            # Drop orphaned end markers in clear/remove mode
            if (clear_mode or remove_mode) and is_end_marker(line):
                changed = True
            else:
                output.append(line)
            i += 1

    # Write if content changed
    if output != original_lines:
        with open(source_file, "w") as f:
            f.writelines(output)
        print(f"Updated file: {source_file}")

    # Extra step for --remove: strip all marker lines
    if remove_mode:
        with open(source_file, "r") as f:
            lines_after_clear = f.readlines()

        final_lines = []

        for line in lines_after_clear:
            is_start = is_start_marker(line)
            end_result = is_end_marker(line)

            # Extract block type from is_end_marker's return value
            if end_result[0]:  # If it's an end marker
                block_type = end_result[1]  # Set block_type to the returned string

            # Include the line in final_lines only if it's neither a start nor an end marker
            if not (is_start or end_result[0]):
                final_lines.append(line)

        if final_lines != lines_after_clear:
            with open(source_file, "w") as f:
                f.writelines(final_lines)
            print(f"Removed all block markers from: {source_file}")


def process_path(path, insert_path, clear_mode=False, remove_mode=False):
    path = Path(path).expanduser().resolve()
    insert_path = Path(insert_path).expanduser().resolve()

    if not path.exists():
        print(f"Error: Source path '{path}' does not exist.")
        return
    if not insert_path.is_dir():
        print(f"Error: Insert path '{insert_path}' is not a directory.")
        return

    if path.is_file():
        process_file(path, insert_path, clear_mode, remove_mode)
    else:
        for file in path.rglob("*.py"):
            process_file(file, insert_path, clear_mode, remove_mode)
        for md_file in path.rglob("*.md"):
            process_file(md_file, insert_path, clear_mode, remove_mode)


def main():
    parser = argparse.ArgumentParser(description="Insert code blocks into Python files based on markers.")
    parser.add_argument("--source_path", required=True, help="Source file or directory.")
    parser.add_argument("--insert_path", required=True, help="Base path for block files.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--clear", action="store_true", help="Clear blocks without insertion.")
    group.add_argument("--remove", action="store_true", help="Clear blocks and then remove all marker lines.")
    args = parser.parse_args()

    process_path(args.source_path, args.insert_path, args.clear, args.remove)


if __name__ == "__main__":
    main()
