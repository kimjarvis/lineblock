import re
from pathlib import Path

from lineblock.common import Common
from lineblock.defaults import Defaults
from lineblock.exceptions import OrphanedInsertEndMarkerError


class BlockInsert(Common):
    def __init__(
        self,
        source_file: str,
        insert_directory_prefix: str,
        output_directory: str = None,
        clear_mode: bool = False,
        insert_begin_prefix: str = None,
        insert_begin_suffix: str = None,
        insert_end_prefix: str = None,
        insert_end_suffix: str = None,
        before: str = None,
        after: str = None,
    ):
        self.source_file = source_file
        self.insert_directory_prefix = insert_directory_prefix
        self.output_directory = output_directory
        self.clear_mode = clear_mode
        self.insert_begin_prefix = insert_begin_prefix
        self.insert_begin_suffix = insert_begin_suffix
        self.insert_end_prefix = insert_end_prefix
        self.insert_end_suffix = insert_end_suffix
        self.before = before
        self.after = after

        self.markers: dict = None

    def is_end_marker(self, line):
        s = line.strip()
        if re.fullmatch(rf"{self.markers["Insert"]["End"]["Prefix"]}.*?{self.markers["Insert"]["End"]["Suffix"]}.*", s):
            return True
        return False

    def extract_block_info(self, marker_line):
        match = re.match(
            rf"(\s*){self.markers["Insert"]["Begin"]["Prefix"]}\s+(\S+)(?:\s+(-?\d+))?{self.markers["Insert"]["Begin"]["Suffix"]}.*", marker_line
        )
        if match:
            leading_ws = match.group(1)
            file_name = match.group(2)
            extra_indent = int(match.group(3)) if match.group(3) else 0
            original_indent = len(leading_ws)
            total_indent = original_indent + extra_indent
            file_path = Path(self.insert_directory_prefix) / file_name
            return file_path, total_indent, original_indent, "markdown"

        return None

    def process_file(self, source_root=None):
        try:
            with open(self.source_file, "r") as f:
                original_lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: Source file '{self.source_file}' not found.")
            return

        output = []
        i = 0
        changed = False
        source_file_path = Path(self.source_file).resolve()

        # Track if we're inside a block (to detect orphaned end markers)
        inside_block = False

        # Determine output path
        if self.output_directory is None:
            # In-place modification
            output_path = source_file_path
        else:
            # Write to output directory preserving relative structure
            output_root = Path(self.output_directory).resolve()
            if source_root is None:
                # Single file case: output directly to output_root/filename
                output_path = output_root / source_file_path.name
            else:
                # Directory case: preserve relative path under output_root
                rel_path = source_file_path.relative_to(source_root)
                output_path = output_root / rel_path

        while i < len(original_lines):
            line = original_lines[i]

            # Check if this is an end marker without a start marker
            if self.is_end_marker(line) and not inside_block:
                # This is an orphaned end marker
                raise OrphanedInsertEndMarkerError(
                    source_file=str(source_file_path),
                    line_number=i + 1,
                    line_content=line.strip(),
                )

            info = self.extract_block_info(line)

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
                    if self.is_end_marker(original_lines[j]):
                        end_i = j
                        break

                next_i = (end_i + 1) if end_i is not None else (i + 1)

                if self.clear_mode:
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
                        if not line.endswith("\n"):
                            replacement.append("\n")

                        # Process the block content with proper indentation
                        indented_block = self.indent_lines(block_content, total_indent)

                        # Ensure each line of inserted content ends with newline
                        formatted_indented_block = []
                        for indented_line in indented_block:
                            stripped_line = indented_line.rstrip("\n")
                            formatted_indented_block.append(stripped_line + "\n")

                        replacement.extend(formatted_indented_block)
                    except FileNotFoundError:
                        print(f"Warning: Block file '{file_path}' not found.")

                    block_end_tag = f"{' ' * orig_indent}{self.markers["Insert"]["End"]["Marker"]}"
                    # print(block_end_tag) 

                    # if block_type == "python":
                    #     block_end_tag = f"{' ' * orig_indent}# end insert"
                    # else:
                    #     block_end_tag = f"{' ' * orig_indent}<!-- end insert -->"


                    # Only add newline to the block end tag if the original marker line had a newline
                    if line.endswith("\n"):
                        replacement.append(block_end_tag + "\n")
                    else:
                        replacement.append(block_end_tag)

                    output.extend(replacement)
                    changed = True

                # Set inside_block to True when we find a start marker
                inside_block = True
                i = next_i
            else:
                if self.is_end_marker(line):
                    # We've reached the end of a block
                    inside_block = False

                if self.clear_mode and self.is_end_marker(line):
                    changed = True
                else:
                    output.append(line)
                i += 1

        # Write output if changed
        if output != original_lines:
            # Ensure output directory exists - raise exception if it doesn't
            if not output_path.parent.exists():
                raise FileNotFoundError(
                    f"Output directory '{output_path.parent}' does not exist."
                )
            with open(output_path, "w") as f:
                f.writelines(output)
            action = "Created" if self.output_directory else "Updated"
            print(f"{action} file: {output_path}")

    def process(self):
        source_file_path = Path(self.source_file).expanduser().resolve()
        insert_dir_path = Path(self.insert_directory_prefix).expanduser().resolve()

        if not source_file_path.exists():
            raise FileNotFoundError(f"Source path '{source_file_path}' does not exist.")

        # Ensure source_file is a file
        if not source_file_path.is_file():
            raise ValueError(
                f"Source path '{source_file_path}' must be a file, not a directory."
            )

        # Ensure source_file has either .py or .md extension
        if source_file_path.suffix.lower() not in [".py", ".md"]:
            raise ValueError(
                f"Source path '{source_file_path}' must be a .py or .md file, not '{source_file_path.suffix}'."
            )

        # Ensure insert_directory_prefix is a directory
        if not insert_dir_path.is_dir():
            raise NotADirectoryError(
                f"Insert path '{insert_dir_path}' is not a directory."
            )

        # Resolve output path if provided
        output_root = None
        if self.output_directory:
            output_root = Path(self.output_directory).expanduser().resolve()
            # Ensure output_directory exists
            if not output_root.exists():
                raise FileNotFoundError(
                    f"Output directory '{output_root}' does not exist."
                )
            # Ensure output_directory is a directory
            if not output_root.is_dir():
                raise NotADirectoryError(
                    f"Output path '{self.output_directory}' must be a directory, not a file."
                )

            # Check that source file is not within the output directory
            try:
                source_file_path.relative_to(output_root)
                raise ValueError(
                    f"Source file '{source_file_path}' must not be inside output directory '{output_root}'."
                )
            except ValueError:
                # Expected case: source_file is NOT inside output_root
                pass

        # Update instance fields with resolved paths
        self.source_file = str(source_file_path)
        self.insert_directory_prefix = str(insert_dir_path)
        if self.output_directory:
            self.output_directory = str(output_root)

        self.markers = Defaults.get_markers(Path(self.source_file).suffix)

        print(self.markers["Insert"]["Begin"]["Prefix"])

        self.process_file()


def block_insert(
    source_file: str,
    insert_directory_prefix: str,
    output_directory: str = None,
    clear_mode: bool = False,
    insert_begin_prefix: str = None,
    insert_begin_suffix: str = None,
    insert_end_prefix: str = None,
    insert_end_suffix: str = None,
    before: str = None,
    after: str = None,
):
    """Insert code blocks into Python/Markdown files based on markers."""
    block_inserter = BlockInsert(
        source_file=source_file,
        insert_directory_prefix=insert_directory_prefix,
        output_directory=output_directory,
        clear_mode=clear_mode,
        insert_begin_prefix=insert_begin_prefix,
        insert_begin_suffix=insert_begin_suffix,
        insert_end_prefix=insert_end_prefix,
        insert_end_suffix=insert_end_suffix,
        before=before,
        after=after,
    )
    try:
        block_inserter.process()
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
