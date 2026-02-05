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
    ):
        self.source_file = source_file
        self.insert_directory_prefix = insert_directory_prefix
        self.output_directory = output_directory
        self.clear_mode = clear_mode
        self.insert_begin_prefix = insert_begin_prefix
        self.insert_begin_suffix = insert_begin_suffix
        self.insert_end_prefix = insert_end_prefix
        self.insert_end_suffix = insert_end_suffix

        self.markers: dict = None

    def is_end_marker(self, line):
        s = line.strip()
        if re.fullmatch(rf"{self.markers["Insert"]["End"]["Prefix"]}.*?{self.markers["Insert"]["End"]["Suffix"]}.*", s):
            return True
        return False

    def extract_block_info(self, marker_line):
        # Pattern: leading_ws + prefixmarker + filename + [optional indent] + [optional skip] + [optional hop] + suffixmarker + [anything]
        match = re.match(
            rf"(\s*){self.markers['Insert']['Begin']['Prefix']}\s+(\S+)(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*{self.markers['Insert']['Begin']['Suffix']}.*",
            marker_line
        )
        if match:
            leading_ws = match.group(1)
            file_name = match.group(2)
            extra_indent = int(match.group(3)) if match.group(3) else 0
            hop = int(match.group(4)) if match.group(4) else 0
            skip = int(match.group(5)) if match.group(5) else 0
            original_indent = len(leading_ws)
            total_indent = original_indent + extra_indent
            file_path = Path(self.insert_directory_prefix) / file_name

            return file_path, total_indent, original_indent, hop, skip

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
                file_path, total_indent, orig_indent, hop, skip = info
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

                # Calculate actual hop and skip values based on available lines
                # If no end marker exists, consider all lines after the start marker
                available_lines = (end_i - (i + 1)) if end_i is not None else len(original_lines) - (i + 1)
                actual_hop = min(hop, available_lines) if available_lines >= 0 else 0
                after_hop_idx = i + 1 + actual_hop if actual_hop > 0 else i + 1

                # Calculate available lines after hop for skip
                available_lines_after_hop = (end_i - after_hop_idx) if end_i is not None else len(original_lines) - after_hop_idx
                actual_skip = min(skip, available_lines_after_hop) if available_lines_after_hop >= 0 else 0

                # Calculate next_i based on whether there's an end marker or not
                # But in clear mode when there's no end marker, we shouldn't skip lines
                if end_i is not None:
                    next_i = end_i + 1
                elif self.clear_mode:
                    # In clear mode with no end marker, don't skip any lines
                    next_i = i + 1
                else:
                    # When there's no end marker in normal mode, skip the hop and skip lines
                    next_i = i + 1 + actual_hop + actual_skip

                if self.clear_mode:
                    # In clear mode, we restore the original file structure
                    # If there's no end marker, this means no insertion has occurred yet,
                    # so we just output the marker and continue normally
                    if end_i is None:
                        # No end marker means no insertion has occurred, just output the marker line
                        output.append(line)
                        # Move to the next line to continue processing normally
                        i += 1
                    else:
                        # There is an end marker, so insertion has occurred
                        # Output the marker line
                        output.append(line)

                        # Output the hop lines (they remain in the same relative position after marker)
                        for j in range(i + 1, i + 1 + actual_hop):
                            if j < len(original_lines):
                                output.append(original_lines[j])

                        # Output the skip lines (they were moved to before the end marker)
                        # The skip lines are the 'actual_skip' lines immediately before the end marker
                        skip_start_idx = end_i - actual_skip
                        for j in range(skip_start_idx, end_i):
                            if j >= 0 and j < len(original_lines):
                                output.append(original_lines[j])

                        # Move to the next position after the end marker in the current file
                        i = next_i

                    changed = True
                else:
                    # Check if the block is already inserted by comparing content between markers
                    block_already_inserted = False
                    if end_i is not None:
                        # Get the content between the marker and end marker that should contain the block
                        # This content should be: hop lines + block content + skip lines
                        start_content_idx = i + 1
                        end_content_idx = end_i

                        # Extract the content between markers
                        between_content = original_lines[start_content_idx:end_content_idx]

                        try:
                            # Load the expected block content
                            with open(file_path, "r") as f:
                                expected_block_content = f.readlines()

                            # Apply indentation to expected block content
                            expected_indented_block = self.indent_lines(expected_block_content, total_indent)
                            expected_formatted_block = []
                            for indented_line in expected_indented_block:
                                stripped_line = indented_line.rstrip("\n")
                                expected_formatted_block.append(stripped_line + "\n")

                            # Check if the between_content matches the expected pattern:
                            # [hop lines] + [expected block content] + [skip lines]
                            expected_hop_lines = original_lines[i + 1:i + 1 + actual_hop]
                            expected_skip_lines = original_lines[end_content_idx - actual_skip:end_content_idx]

                            # Extract the middle part (should be the block content)
                            middle_start = len(expected_hop_lines)
                            middle_end = len(between_content) - len(expected_skip_lines)
                            if middle_end < middle_start:
                                middle_end = middle_start  # Prevent negative slice
                            actual_block_content = between_content[middle_start:middle_end]

                            # Compare the actual block content with expected
                            if actual_block_content == expected_formatted_block:
                                block_already_inserted = True
                        except FileNotFoundError:
                            # If block file doesn't exist, we can't check if already inserted
                            pass

                    if block_already_inserted:
                        # Block is already inserted, just copy the whole section as-is
                        for idx in range(i, next_i):
                            output.append(original_lines[idx])
                    else:
                        # Block is not inserted yet, proceed with insertion
                        # Always add the marker line as-is initially
                        replacement = [line]

                        try:
                            with open(file_path, "r") as f:
                                block_content = f.readlines()

                            # If the original marker line doesn't end with \n,
                            # we need to add a newline before the block content for proper formatting
                            if not line.endswith("\n"):
                                replacement.append("\n")

                            # Apply hop: insert original lines before the block
                            for j in range(i + 1, i + 1 + actual_hop):
                                replacement.append(original_lines[j])

                            # Process the block content with proper indentation
                            indented_block = self.indent_lines(block_content, total_indent)

                            # Ensure each line of inserted content ends with newline
                            formatted_indented_block = []
                            for indented_line in indented_block:
                                stripped_line = indented_line.rstrip("\n")
                                formatted_indented_block.append(stripped_line + "\n")

                            replacement.extend(formatted_indented_block)

                            # Apply skip: insert original lines after the block but before end marker
                            for j in range(after_hop_idx, after_hop_idx + actual_skip):
                                replacement.append(original_lines[j])

                            # When there's no end marker, we need to handle the remaining lines differently
                            # We don't add them to replacement as they'll be handled by the main loop
                            # We just need to make sure the main loop index is updated correctly later
                        except FileNotFoundError:
                            print(f"Warning: Block file '{file_path}' not found.")

                        block_end_tag = f"{' ' * orig_indent}{self.markers["Insert"]["End"]["Marker"]}"

                        # Add newline to the block end tag only if the original marker line had a newline
                        if line.endswith("\n"):
                            replacement.append(block_end_tag + "\n")
                        else:
                            replacement.append(block_end_tag)

                        output.extend(replacement)
                        changed = True

                    # Update i to skip over the processed content
                    i = next_i

                # Set inside_block to True when we find a start marker
                inside_block = True
                i = next_i
            else:
                if self.is_end_marker(line):
                    # We've reached the end of a block
                    inside_block = False

                if self.clear_mode and self.is_end_marker(line):
                    # In clear mode, skip the end marker as we're removing it
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
    )
    try:
        block_inserter.process()
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
