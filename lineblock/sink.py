import re
from pathlib import Path

from lineblock.common import Common
from lineblock.exceptions import OrphanedInsertEndMarkerError
from lineblock.markers import Markers

class Sink(Common):
    def __init__(
        self,
        source_file: Path = None,
        markers: dict = None,
        block_map: list = None,
    ):
        self.source_file = source_file
        self.markers = markers
        self.block_map = block_map


        self.clear_mode=False

    def is_end_marker(self, line):
        s = line.strip()
        if re.fullmatch(self.markers["Insert"]["End"], s):
            return True
        return False


    def extract_block_info(self, line):
        # Pattern: leading_ws + prefixmarker + identity + [optional indent] + [optional head] + [optional tail] + suffixmarker + [anything]
        match = re.match(self.markers["Insert"]["Begin"], line)
        if match:
            leading_ws = match.group(1)

            # Identity can be in group 2 (double quotes), 3 (single quotes), or 4 (unquoted word)
            identity = match.group(2) or match.group(3) or match.group(4)

            extra_indent = int(match.group(5)) if match.group(5) else 0
            head = int(match.group(6)) if match.group(6) else 0
            tail = int(match.group(7)) if match.group(7) else 0

            original_indent = len(leading_ws)
            total_indent = original_indent + extra_indent
            return True, identity, original_indent, total_indent, head, tail
        return False, None, 0, 0, 0, 0  # Return consistent tuple


    def process_file(self):
        try:
            with open(self.source_file, "r") as f:
                original_lines = f.readlines()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Source file '{self.path}' not found.") from e

        output = []
        i = 0
        changed = False
        source_file_path = Path(self.source_file).resolve()

        # Track if we're inside a block (to detect orphaned end markers)
        inside_block = False

        output_path = source_file_path

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

            if info[0]:
                _, identity, orig_indent, total_indent, head, tail = info

                # Find end marker
                end_i = None
                for j in range(i + 1, len(original_lines)):
                    if self.is_end_marker(original_lines[j]):
                        end_i = j
                        break

                # Calculate actual head and tail values based on available lines
                # If no end marker exists, consider all lines after the start marker
                available_lines = (end_i - (i + 1)) if end_i is not None else len(original_lines) - (i + 1)
                actual_head = min(head, available_lines) if available_lines >= 0 else 0
                after_head_idx = i + 1 + actual_head if actual_head > 0 else i + 1

                # Calculate available lines after head for tail
                available_lines_after_head = (end_i - after_head_idx) if end_i is not None else len(original_lines) - after_head_idx
                actual_tail = min(tail, available_lines_after_head) if available_lines_after_head >= 0 else 0

                # Calculate next_i based on whether there's an end marker or not
                # But in clear mode when there's no end marker, we shouldn't skip lines
                if end_i is not None:
                    next_i = end_i + 1
                elif self.clear_mode:
                    # In clear mode with no end marker, don't skip any lines
                    next_i = i + 1
                else:
                    # When there's no end marker in normal mode, skip the head and tail lines
                    next_i = i + 1 + actual_head + actual_tail

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

                        # Output the head lines (they remain in the same relative position after marker)
                        for j in range(i + 1, i + 1 + actual_head):
                            if j < len(original_lines):
                                output.append(original_lines[j])

                        # Output the tail lines (they were moved to before the end marker)
                        # The tail lines are the 'actual_tail' lines immediately before the end marker
                        tail_start_idx = end_i - actual_tail
                        for j in range(tail_start_idx, end_i):
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
                        # This content should be: head lines + block content + tail lines
                        start_content_idx = i + 1
                        end_content_idx = end_i

                        # Extract the content between markers
                        between_content = original_lines[start_content_idx:end_content_idx]

                        try:
                            for item in self.block_map:
                                if item["identity"] == identity:
                                    expected_block_content = item["block"]
                                    break
                            else:
                                raise ValueError(f"Identity '{identity}' not found in block map")

                            # Apply indentation to expected block content
                            expected_indented_block = self.indent_lines(expected_block_content, total_indent)
                            expected_formatted_block = []
                            for indented_line in expected_indented_block:
                                stripped_line = indented_line.rstrip("\n")
                                expected_formatted_block.append(stripped_line + "\n")

                            # Check if the between_content matches the expected pattern:
                            # [head lines] + [expected block content] + [tail lines]
                            expected_head_lines = original_lines[i + 1:i + 1 + actual_head]
                            expected_tail_lines = original_lines[end_content_idx - actual_tail:end_content_idx]

                            # Extract the middle part (should be the block content)
                            middle_start = len(expected_head_lines)
                            middle_end = len(between_content) - len(expected_tail_lines)
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

                        for item in self.block_map:
                            if item["identity"] == identity:
                                block_content = item["block"]
                                break
                        else:
                            raise ValueError(f"Identity '{identity}' not found in block map")

                        # If the original marker line doesn't end with \n,
                        # we need to add a newline before the block content for proper formatting
                        if not line.endswith("\n"):
                            replacement.append("\n")

                        # Apply head: insert original lines before the block
                        for j in range(i + 1, i + 1 + actual_head):
                            replacement.append(original_lines[j])

                        # Process the block content with proper indentation
                        indented_block = self.indent_lines(block_content, total_indent)

                        # Ensure each line of inserted content ends with newline
                        formatted_indented_block = []
                        for indented_line in indented_block:
                            stripped_line = indented_line.rstrip("\n")
                            formatted_indented_block.append(stripped_line + "\n")

                        replacement.extend(formatted_indented_block)

                        # Apply tail: insert original lines after the block but before end marker
                        for j in range(after_head_idx, after_head_idx + actual_tail):
                            replacement.append(original_lines[j])

                        # When there's no end marker, we need to handle the remaining lines differently
                        # We don't add them to replacement as they'll be handled by the main loop
                        # We just need to make sure the main loop index is updated correctly later

                        block_end_tag = f"{' ' * orig_indent}{self.markers["Insert"]["Marker"]}"

                        # Add newline to the block end tag only if the original marker line had a newline
                        if line.endswith("\n"):
                            replacement.append(block_end_tag + "\n")
                        else:
                            replacement.append(block_end_tag)

                        output.extend(replacement)
                        changed = True

                    # Update i to tail over the processed content
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
            with open(output_path, "w") as f:
                f.writelines(output)
            print(f"Updated file: {output_path}")