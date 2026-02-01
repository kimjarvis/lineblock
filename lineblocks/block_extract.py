import argparse
import re
from pathlib import Path

from lineblocks.exceptions import OrphanedExtractEndMarkerError, UnclosedBlockError
from lineblocks.common import Common

class BlockExtract(Common):
    def __init__(self):
        pass

    @staticmethod
    def is_start_marker(line):
        s = line.strip()
        if re.fullmatch(r"#\s*block extract\s+\S+.*", s):
            return True
        if re.fullmatch(r"<!--\s*block extract\s+\S+.*-->", s):
            return True
        return False

    @staticmethod
    def is_end_marker(line):
        s = line.strip()
        if re.fullmatch(r"#\s*end extract\s*", s):
            return True
        if re.fullmatch(r"<!--\s*end extract\s*-->", s):
            return True
        return False


    @staticmethod
    def extract_block_info(marker_line, extract_directory_prefix):
        match = re.match(r"(\s*)#\s*block extract\s+(\S+)(?:\s+(-?\d+))?", marker_line)
        if match:
            leading_ws = match.group(1)
            file_name = match.group(2)
            extra_indent = int(match.group(3)) if match.group(3) else 0
            original_indent = len(leading_ws)
            total_indent = original_indent + extra_indent
            file_path = Path(extract_directory_prefix) / file_name
            return file_path, total_indent

        match = re.match(r"(\s*)<!--\s*block extract\s+(\S+)(?:\s+(-?\d+))?\s*-->", marker_line)
        if match:
            leading_ws = match.group(1)
            file_name = match.group(2)
            extra_indent = int(match.group(3)) if match.group(3) else 0
            original_indent = len(leading_ws)
            total_indent = original_indent + extra_indent
            file_path = Path(extract_directory_prefix) / file_name
            return file_path, total_indent

        return None

    def process_file(self, source_file, extract_directory_prefix):
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

            if self.is_end_marker(line):
                # Check if we have an orphaned end marker
                if not in_block:
                    raise OrphanedExtractEndMarkerError(source_file, i + 1, line.strip())
                else:
                    # Found the end of the current block
                    in_block = False
                    i += 1
                    continue

            if self.is_start_marker(line):
                # Check if we're already in a block (nested blocks are not allowed)
                if in_block:
                    # We're trying to start a new block while already in one
                    raise OrphanedExtractEndMarkerError(source_file, i + 1,
                                                        "Found block extract marker without closing previous block.")

                info = self.extract_block_info(line, extract_directory_prefix)
                if info:
                    file_path, total_indent = info
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
                        raise UnclosedBlockError(source_file, start_line, line.strip())

                    # Check if parent directories exist (don't create them)
                    if not file_path.parent.exists():
                        raise ValueError(f"Parent directory does not exist for output file: '{file_path}'")

                    # Write extracted block with indentation
                    indented_lines = self.indent_lines(block_lines, total_indent)
                    with open(file_path, "w") as out_f:
                        out_f.writelines(indented_lines)
            i += 1

    def process_path(self, path, extract_directory_prefix):
        path = Path(path).expanduser().resolve()
        extract_directory_prefix = Path(extract_directory_prefix).expanduser().resolve()

        # Raise FileNotFoundError if the source path doesn't exist
        if not path.exists():
            raise FileNotFoundError(f"Error: Source path '{path}' does not exist.")

        # Raise FileNotFoundError if the extract directory doesn't exist
        if not extract_directory_prefix.exists():
            raise FileNotFoundError(f"Error: Extract path '{extract_directory_prefix}' does not exist.")

        # Raise an error if extract_directory_prefix exists but is not a directory
        if not extract_directory_prefix.is_dir():
            raise NotADirectoryError(f"Error: Extract path '{extract_directory_prefix}' is not a directory.")

        if path.is_file():
            self.process_file(path, extract_directory_prefix)
        else:
            for file in path.rglob("*.py"):
                self.process_file(file, extract_directory_prefix)


def block_extract(source_path, extract_directory_prefix):
    try:
        extractor = BlockExtract()
        extractor.process_path(source_path, extract_directory_prefix)
    except (UnclosedBlockError, OrphanedExtractEndMarkerError) as e:
        print(f"Error: {e}")
        raise  # Re-raise to exit with non-zero status
    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        print(f"Error: {e}")
        raise  # Re-raise to exit with non-zero status
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


