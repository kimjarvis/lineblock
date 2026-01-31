import argparse
import re
from pathlib import Path


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

def extract_block_info(marker_line, insert_path):
    match = re.match(r"(\s*)#\s*block insert\s+(\S+)(?:\s+(-?\d+))?", marker_line)
    if match:
        leading_ws = match.group(1)
        file_name = match.group(2)
        extra_indent = int(match.group(3)) if match.group(3) else 0
        original_indent = len(leading_ws)
        total_indent = original_indent + extra_indent
        file_path = Path(insert_path) / file_name
        return file_path, total_indent, original_indent, "python"

    match = re.match(r"(\s*)<!--\s*block insert\s+(\S+)(?:\s+(-?\d+))?\s*-->", marker_line)
    if match:
        leading_ws = match.group(1)
        file_name = match.group(2)
        extra_indent = int(match.group(3)) if match.group(3) else 0
        original_indent = len(leading_ws)
        total_indent = original_indent + extra_indent
        file_path = Path(insert_path) / file_name
        return file_path, total_indent, original_indent, "markdown"

    return None


def is_start_marker(line):
    s = line.strip()
    if re.fullmatch(r"#\s*block insert\s+\S+.*", s):
        return True, "python"
    if re.fullmatch(r"<!--\s*block insert\s+\S+.*-->", s):
        return True, "markdown"
    return False, None


def is_end_marker(line):
    s = line.strip()
    if re.fullmatch(r"#\s*block end\s*", s):
        return True
    if re.fullmatch(r"<!--\s*block end\s*-->", s):
        return True
    return False


def process_file(source_file, insert_path, output_root=None, source_root=None, clear_mode=False):
    try:
        with open(source_file, "r") as f:
            original_lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Source file '{source_file}' not found.")
        return

    output = []
    i = 0
    changed = False
    source_path = Path(source_file).resolve()

    # Determine output path
    if output_root is None:
        # In-place modification
        output_path = source_path
    else:
        # Write to output directory preserving relative structure
        if source_root is None:
            # Single file case: output directly to output_root/filename
            output_path = output_root / source_path.name
        else:
            # Directory case: preserve relative path under output_root
            rel_path = source_path.relative_to(source_root)
            output_path = output_root / rel_path

    while i < len(original_lines):
        line = original_lines[i]
        info = extract_block_info(line, insert_path)

        if info:
            file_path, total_indent, orig_indent, block_type = info
            file_exists = file_path.exists()

            if not file_exists:
                print(f"Warning: Block file '{file_path}' not found.")
                output.append(line)
                i += 1
                continue

            # Find end marker
            end_i = None
            for j in range(i + 1, len(original_lines)):
                if is_end_marker(original_lines[j]):
                    end_i = j
                    break

            next_i = (end_i + 1) if end_i is not None else (i + 1)

            if clear_mode:
                output.append(line)
                changed = True
            else:
                # Always add the marker line as-is initially
                replacement = [line]

                try:
                    with open(file_path, "r") as f:
                        block_content = f.readlines()

                    # If the original marker line doesn't end with \n,
                    # we need to add a newline before the block content for proper formatting
                    if not line.endswith('\n'):
                        replacement.append('\n')

                    # Process the block content with proper indentation
                    # Ensure each line of the inserted content has a newline for proper formatting
                    indented_block = indent_lines(block_content, total_indent)

                    # For proper formatting, ensure each line of inserted content ends with newline
                    formatted_indented_block = []
                    for idx, indented_line in enumerate(indented_block):
                        stripped_line = indented_line.rstrip('\n')
                        # Add newline to all lines for proper formatting
                        formatted_indented_block.append(stripped_line + '\n')

                    replacement.extend(formatted_indented_block)
                except FileNotFoundError:
                    print(f"Warning: Block file '{file_path}' not found.")

                if block_type == "python":
                    block_end_tag = f"{' ' * orig_indent}# block end"
                else:
                    block_end_tag = f"{' ' * orig_indent}<!-- block end -->"

                # Only add newline to the block end tag if the original marker line had a newline
                if line.endswith('\n'):
                    replacement.append(block_end_tag + "\n")
                else:
                    replacement.append(block_end_tag)

                output.extend(replacement)
                changed = True

            i = next_i
        else:
            if clear_mode and is_end_marker(line):
                changed = True
            else:
                output.append(line)
            i += 1

    # Write output if changed
    if output != original_lines:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.writelines(output)
        action = "Created" if output_root else "Updated"
        print(f"{action} file: {output_path}")


def process_path(source_path, insert_path, output_path=None, clear_mode=False):
    source_path = Path(source_path).expanduser().resolve()
    insert_path = Path(insert_path).expanduser().resolve()

    if not source_path.exists():
        print(f"Error: Source path '{source_path}' does not exist.")
        return
    if not insert_path.is_dir():
        print(f"Error: Insert path '{insert_path}' is not a directory.")
        return

    # Resolve output path if provided
    output_root = Path(output_path).expanduser().resolve() if output_path else None
    if output_root and not output_root.exists():
        output_root.mkdir(parents=True, exist_ok=True)

    # Prevent processing files inside output directory when scanning source directory
    if source_path.is_dir() and output_root:
        if output_root.resolve() in source_path.resolve().parents or output_root == source_path.resolve():
            print(f"Error: Output path must not be inside or equal to source path")
            return

    if source_path.is_file():
        # Skip if this file is inside the output directory (prevent recursive processing)
        if output_root and source_path.resolve().parent == output_root.resolve():
            return
        process_file(source_path, insert_path, output_root=output_root, clear_mode=clear_mode)
    else:
        # Directory processing: collect source files excluding output directory contents
        source_root = source_path
        py_files = [f for f in source_path.rglob("*.py")
                    if not (output_root and output_root in f.resolve().parents)]
        md_files = [f for f in source_path.rglob("*.md")
                    if not (output_root and output_root in f.resolve().parents)]

        for file in py_files:
            process_file(file, insert_path, output_root=output_root, source_root=source_root, clear_mode=clear_mode)
        for file in md_files:
            process_file(file, insert_path, output_root=output_root, source_root=source_root, clear_mode=clear_mode)


def block_insert(source_path: str, insert_path: str, output_path: str = None, clear_mode: bool = False):
    """Insert code blocks into Python/Markdown files based on markers.

    Args:
        source_path (str): Source file or directory.
        insert_path (str): Base path for block files.
        output_path (str, optional): Directory where generated files will be written.
            If None, source files are modified in-place.
        clear_mode (bool): Clear blocks without insertion.
    """
    process_path(source_path, insert_path, output_path, clear_mode)


def main():
    parser = argparse.ArgumentParser(description="Insert code blocks into Python/Markdown files based on markers.")
    parser.add_argument("--source_path", required=True, help="Source file or directory.")
    parser.add_argument("--insert_path", required=True, help="Base path for block files.")
    parser.add_argument("--output_path",
                        help="Directory for generated files (preserves structure). If omitted, modifies sources in-place.")
    parser.add_argument("--clear", action="store_true", help="Clear blocks without insertion.")
    args = parser.parse_args()

    # Execute block insertion
    block_insert(
        source_path=args.source_path,
        insert_path=args.insert_path,
        output_path=args.output_path,
        clear_mode=args.clear
    )


if __name__ == "__main__":
    main()