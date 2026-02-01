import argparse
import re
from pathlib import Path

from lineblock.exceptions import OrphanedInsertEndMarkerError
from lineblock.common import Common


class BlockInsert(Common):
    @staticmethod
    def is_start_marker(line):
        s = line.strip()
        if re.fullmatch(r"#\s*block insert\s+\S+.*", s):
            return True, "python"
        if re.fullmatch(r"<!--\s*block insert\s+\S+.*-->", s):
            return True, "markdown"
        return False, None

    @staticmethod
    def is_end_marker(line):
        s = line.strip()
        if re.fullmatch(r"#\s*end insert\s*", s):
            return True
        if re.fullmatch(r"<!--\s*end insert\s*-->", s):
            return True
        return False


    @staticmethod
    def extract_block_info(marker_line, insert_directory_prefix):
        match = re.match(r"(\s*)#\s*block insert\s+(\S+)(?:\s+(-?\d+))?", marker_line)
        if match:
            leading_ws = match.group(1)
            file_name = match.group(2)
            extra_indent = int(match.group(3)) if match.group(3) else 0
            original_indent = len(leading_ws)
            total_indent = original_indent + extra_indent
            file_path = Path(insert_directory_prefix) / file_name
            return file_path, total_indent, original_indent, "python"

        match = re.match(r"(\s*)<!--\s*block insert\s+(\S+)(?:\s+(-?\d+))?\s*-->", marker_line)
        if match:
            leading_ws = match.group(1)
            file_name = match.group(2)
            extra_indent = int(match.group(3)) if match.group(3) else 0
            original_indent = len(leading_ws)
            total_indent = original_indent + extra_indent
            file_path = Path(insert_directory_prefix) / file_name
            return file_path, total_indent, original_indent, "markdown"

        return None

    @staticmethod
    def process_file(source_file, insert_directory_prefix, output_root=None, source_root=None, clear_mode=False):
        try:
            with open(source_file, "r") as f:
                original_lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: Source file '{source_file}' not found.")
            return

        output = []
        i = 0
        changed = False
        source_file = Path(source_file).resolve()

        # Track if we're inside a block (to detect orphaned end markers)
        inside_block = False

        # Determine output path
        if output_root is None:
            # In-place modification
            output_directory = source_file
        else:
            # Write to output directory preserving relative structure
            if source_root is None:
                # Single file case: output directly to output_root/filename
                output_directory = output_root / source_file.name
            else:
                # Directory case: preserve relative path under output_root
                rel_path = source_file.relative_to(source_root)
                output_directory = output_root / rel_path

        while i < len(original_lines):
            line = original_lines[i]

            # Check if this is an end marker without a start marker
            if BlockInsert.is_end_marker(line) and not inside_block:
                # This is an orphaned end marker
                raise OrphanedInsertEndMarkerError(
                    source_file=str(source_file),
                    line_number=i + 1,
                    line_content=line.strip()
                )

            info = BlockInsert.extract_block_info(line, insert_directory_prefix)

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
                    if BlockInsert.is_end_marker(original_lines[j]):
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
                        indented_block = BlockInsert.indent_lines(block_content, total_indent)

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
                        block_end_tag = f"{' ' * orig_indent}# end insert"
                    else:
                        block_end_tag = f"{' ' * orig_indent}<!-- end insert -->"

                    # Only add newline to the block end tag if the original marker line had a newline
                    if line.endswith('\n'):
                        replacement.append(block_end_tag + "\n")
                    else:
                        replacement.append(block_end_tag)

                    output.extend(replacement)
                    changed = True

                # Set inside_block to True when we find a start marker
                inside_block = True
                i = next_i
            else:
                if BlockInsert.is_end_marker(line):
                    # We've reached the end of a block
                    inside_block = False

                if clear_mode and BlockInsert.is_end_marker(line):
                    changed = True
                else:
                    output.append(line)
                i += 1

        # Write output if changed
        if output != original_lines:
            # Ensure output directory exists - raise exception if it doesn't
            if not output_directory.parent.exists():
                raise FileNotFoundError(f"Output directory '{output_directory.parent}' does not exist.")
            with open(output_directory, "w") as f:
                f.writelines(output)
            action = "Created" if output_root else "Updated"
            print(f"{action} file: {output_directory}")

    @staticmethod
    def process_path(source_file, insert_directory_prefix, output_directory=None, clear_mode=False):
        source_file = Path(source_file).expanduser().resolve()
        insert_directory_prefix = Path(insert_directory_prefix).expanduser().resolve()

        if not source_file.exists():
            raise FileNotFoundError(f"Source path '{source_file}' does not exist.")

        # Ensure source_file is a file
        if not source_file.is_file():
            raise ValueError(f"Source path '{source_file}' must be a file, not a directory.")

        # Ensure source_file has either .py or .md extension
        if source_file.suffix.lower() not in ['.py', '.md']:
            raise ValueError(f"Source path '{source_file}' must be a .py or .md file, not '{source_file.suffix}'.")

        # Ensure insert_directory_prefix is a directory
        if not insert_directory_prefix.is_dir():
            raise NotADirectoryError(f"Insert path '{insert_directory_prefix}' is not a directory.")

        # Resolve output path if provided
        output_root = None
        if output_directory:
            output_root = Path(output_directory).expanduser().resolve()
            # Ensure output_directory exists - raise exception if it doesn't
            if not output_root.exists():
                raise FileNotFoundError(f"Output directory '{output_root}' does not exist.")
            # Ensure output_directory is a directory
            if not output_root.is_dir():
                raise NotADirectoryError(f"Output path '{output_directory}' must be a directory, not a file.")

            # Check that source file is not within the output directory
            try:
                # Check if source_file is inside output_root
                source_file.relative_to(output_root)
                # If the above doesn't raise an exception, source_file is inside output_root
                raise ValueError(f"Source file '{source_file}' must not be inside output directory '{output_root}'.")
            except ValueError:
                # ValueError is raised if source_file is NOT inside output_root
                # This is the expected case, so we continue
                pass

        BlockInsert.process_file(source_file, insert_directory_prefix, output_root=output_root, clear_mode=clear_mode)


def block_insert(source_file: str, insert_directory_prefix: str, output_directory: str = None,
                 clear_mode: bool = False):
    """Insert code blocks into Python/Markdown files based on markers.
    """
    try:
        BlockInsert.process_path(source_file, insert_directory_prefix, output_directory, clear_mode)
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Error: {e}")
        raise  # Re-raise to exit with non-zero status
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


