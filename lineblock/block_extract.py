import re
from pathlib import Path

from lineblock.common import Common
from lineblock.defaults import Defaults
from lineblock.exceptions import OrphanedExtractEndMarkerError, UnclosedBlockError


class BlockExtract(Common):
    def __init__(
        self,
        source_path: str,
        extract_directory_prefix: str,
        extract_begin_prefix: str = None,
        extract_begin_suffix: str = None,
        extract_end_prefix: str = None,
        extract_end_suffix: str = None,
    ):
        self.source_path = source_path
        self.extract_directory_prefix = extract_directory_prefix
        self.extract_begin_prefix = extract_begin_prefix
        self.extract_begin_suffix = extract_begin_suffix
        self.extract_end_prefix = extract_end_prefix
        self.extract_end_suffix = extract_end_suffix

        self.markers: dict = None

    def is_end_marker(self, line):
        s = line.strip()
        if re.fullmatch(rf"{self.markers["Extract"]["End"]["Prefix"]}.*?{self.markers["Extract"]["End"]["Suffix"]}.*", s):
            return True
        return False

    def extract_block_info(self, marker_line):
        # Pattern: leading_ws + prefixmarker + filename + [optional indent] + [optional head] + [optional tail] + suffixmarker + [anything]
        match = re.match(
            rf"(\s*){self.markers["Extract"]["Begin"]["Prefix"]}\s+(\S+)(?:\s+(-?\d+))?(?:\s+(\d+))?(?:\s+(\d+))?\s*{self.markers["Extract"]["Begin"]["Suffix"]}.*",
            marker_line
        )
        if match:
            leading_ws = match.group(1)
            file_name = match.group(2)
            extra_indent = int(match.group(3)) if match.group(3) else 0
            head = int(match.group(4)) if match.group(4) else 0
            tail = int(match.group(5)) if match.group(5) else 0
            original_indent = len(leading_ws)
            total_indent = (
                    original_indent + extra_indent
            )  # maintains current "extra indent" behavior
            file_path = Path(self.extract_directory_prefix) / file_name
            return True, file_path, total_indent, head, tail
        return False,

    def process_file(self):
        try:
            with open(self.source_path, "r") as f:
                original_lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: Source file '{self.source_path}' not found.")
            return

        i = 0
        in_block = False  # Track if we're currently processing a block
        while i < len(original_lines):
            line = original_lines[i]

            if self.is_end_marker(line):
                # Check if we have an orphaned end marker
                if not in_block:
                    raise OrphanedExtractEndMarkerError(
                        self.source_path, i + 1, line.strip()
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
                        self.source_path,
                        i + 1,
                        "Found block extract marker without closing previous block.",
                    )

                info = self.extract_block_info(line)
                if info:
                    _, file_path, total_indent, head, tail = info
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
                            self.source_path, start_line, line.strip()
                        )

                    # Check if parent directories exist (don't create them)
                    if not file_path.parent.exists():
                        raise ValueError(
                            f"Parent directory does not exist for output file: '{file_path}'"
                        )

                    # Write extracted block with indentation
                    indented_lines = self.indent_lines(block_lines, total_indent)

                    # Ensure there are enough lines after removing head and tail
                    if len(indented_lines) <= (head + tail):
                        raise ValueError("Not enough lines to remove the specified head and tail.")

                    # Remove the top `head` lines and bottom `tail` lines
                    trimmed_lines = indented_lines[head:-tail or None]

                    with open(file_path, "w") as out_f:
                        out_f.writelines(trimmed_lines)
            i += 1

    def process(self):
        path = Path(self.source_path).expanduser().resolve()
        extract_directory_prefix = (
            Path(self.extract_directory_prefix).expanduser().resolve()
        )

        # Raise FileNotFoundError if the source path doesn't exist
        if not path.exists():
            raise FileNotFoundError(f"Error: Source path '{path}' does not exist.")

        # Raise FileNotFoundError if the extract directory doesn't exist
        if not extract_directory_prefix.exists():
            raise FileNotFoundError(
                f"Error: Extract path '{extract_directory_prefix}' does not exist."
            )

        # Raise an error if extract_directory_prefix exists but is not a directory
        if not extract_directory_prefix.is_dir():
            raise NotADirectoryError(
                f"Error: Extract path '{extract_directory_prefix}' is not a directory."
            )

        if path.is_file():
            self.markers = Defaults.get_markers(Path(self.source_path).suffix)
            self.process_file()
        else:
            for file in path.rglob("*.*"):
                self.source_path = file
                if Defaults.check_markers(Path(self.source_path).suffix):
                    self.markers = Defaults.get_markers(Path(self.source_path).suffix)
                    self.process_file()


def block_extract(
    source_path: str,
    extract_directory_prefix: str,
    extract_begin_prefix: str = None,
    extract_begin_suffix: str = None,
    extract_end_prefix: str = None,
    extract_end_suffix: str = None,
):
    try:
        extractor = BlockExtract(
            source_path=source_path,
            extract_directory_prefix=extract_directory_prefix,
            extract_begin_prefix=extract_begin_prefix,
            extract_begin_suffix=extract_begin_suffix,
            extract_end_prefix=extract_end_prefix,
            extract_end_suffix=extract_end_suffix,
        )
        extractor.process()
    except (UnclosedBlockError, OrphanedExtractEndMarkerError) as e:
        print(f"Error: {e}")
        raise  # Re-raise to exit with non-zero status
    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        print(f"Error: {e}")
        raise  # Re-raise to exit with non-zero status
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
