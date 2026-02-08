import re
from pathlib import Path

from lineblock.common import Common
from lineblock.exceptions import OrphanedExtractEndMarkerError, UnclosedBlockError
from lineblock.markers import Markers

class Source(Common):
    def __init__(
        self,
        path: Path = None,
        markers: dict = None
    ):
        self.path = path
        self.markers = markers
        self.block_map = []

    def is_end_marker(self, line):
        s = line.strip()
        if re.fullmatch(self.markers["Extract"]["End"], s):
            return True
        return False

    # Pattern: leading_ws + prefixmarker + identity + [optional indent] + [optional head] + [optional tail] + suffixmarker + [anything]
    def extract_block_info(self, line):
        match = re.match(self.markers["Extract"]["Begin"], line)
        if match:
            leading_ws = match.group(1)

            # Identity can be in group 2 (double quotes), 3 (single quotes), or 4 (unquoted word)
            identity = match.group(2) or match.group(3) or match.group(4)

            extra_indent = int(match.group(5)) if match.group(5) else 0
            head = int(match.group(6)) if match.group(6) else 0
            tail = int(match.group(7)) if match.group(7) else 0

            original_indent = len(leading_ws)
            total_indent = original_indent + extra_indent
            return True, identity, total_indent, head, tail
        return False, None, 0, 0, 0  # Return consistent tuple


    def process_file(self):
        try:
            with open(self.path, "r") as f:
                original_lines = f.readlines()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Source file '{self.path}' not found.") from e

        i = 0
        in_block = False  # Track if we're currently processing a block
        while i < len(original_lines):
            line = original_lines[i]

            if self.is_end_marker(line):
                # Check if we have an orphaned end marker
                if not in_block:
                    raise OrphanedExtractEndMarkerError(
                        self.path, i + 1, line.strip()
                    )
                else:
                    # Found the end of the current block
                    in_block = False
                    i += 1
                    continue

            # if self.is_start_marker(line):
            if self.extract_block_info(line)[0]:
                # Check if we're already in a block (nested blocks are not allowed)
                if in_block:
                    # We're trying to start a new block while already in one
                    raise OrphanedExtractEndMarkerError(
                        self.path,
                        i + 1,
                        "Found block extract marker without closing previous block.",
                    )

                info = self.extract_block_info(line)
                if info:
                    _, identity, total_indent, head, tail = info
                    start_line = i + 1  # 1-based line number for error reporting
                    i += 1
                    block_lines = []
                    in_block = True  # Now we're inside a block

                    # Collect lines until we find the corresponding end marker
                    while i < len(original_lines):
                        current_line = original_lines[i]
                        if self.is_end_marker(current_line):
                            # Found the end marker for this block
                            in_block = False
                            break
                        block_lines.append(current_line)
                        i += 1
                    else:
                        # Reached end of file without finding end marker
                        raise UnclosedBlockError(
                            self.path, start_line, line.strip()
                        )

                    # Write extracted block with indentation
                    indented_lines = self.indent_lines(block_lines, total_indent)

                    # Ensure there are enough lines after removing head and tail
                    if len(indented_lines) <= (head + tail):
                        raise ValueError("Not enough lines to remove the specified head and tail.")

                    # Remove the top `head` lines and bottom `tail` lines
                    trimmed_lines = indented_lines[head:-tail or None]

                    self.block_map.append({
                        "path": self.path,
                        "identity": identity,
                        "start_line": start_line,
                        "end_line": i,
                        "indent": total_indent,
                        "head": head,
                        "tail": tail,
                        "block": trimmed_lines
                    })

            i += 1


