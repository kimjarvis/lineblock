#!/usr/bin/env python3
"""
Path traversal utility. Accepts a file or directory as positional argument.
For directories: supports glob matching, inclusion/exclusion lists.
For files: prints the absolute path of the specified file.
"""

import argparse
import fnmatch
import os
import sys
import traceback
from pathlib import Path
from typing import List, Optional, Union


from lineblock.exceptions import OrphanedInsertEndMarkerError, OrphanedExtractEndMarkerError, UnclosedBlockError, NotAFileError, IncompatibleOptionsError
from lineblock.lineblock import lineblock

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Visit files and print absolute paths. "
                    "Accepts a file or directory as target.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ~/a                          # List all files under directory ~/a
  %(prog)s ~/a -p "*.py"                # Only Python files in ~/a
  %(prog)s ~/a -p "*.txt" -p "*.md"     # Multiple patterns in ~/a
  %(prog)s ~/a -x "*.pyc" -x "__pycache__"  # Exclude patterns in ~/a
  %(prog)s ~/a -d src tests             # Only traverse subdirs src/ and tests/
  %(prog)s specific.txt                 # Print absolute path of specific.txt
        """
    )

    parser.add_argument(
        "path",
        type=str,
        help="Target path (file or directory)"
    )

    parser.add_argument(
        "-p", "--pattern",
        action="append",
        dest="patterns",
        metavar="GLOB",
        help="Glob pattern(s) to match in directory traversal "
             "(can be used multiple times). Default: '*' (all files). "
             "Not allowed when target is a file."
    )

    parser.add_argument(
        "-d", "--dirs",
        nargs="+",
        metavar="SUBDIR",
        help="List of sub-directories to traverse (default: all). "
             "Not allowed when target is a file."
    )

    parser.add_argument(
        "-x", "--exclude",
        action="append",
        dest="excludes",
        metavar="PATTERN",
        help="Exclusion pattern(s), gitignore-style (can be used multiple times). "
             "Not allowed when target is a file."
    )

    parser.add_argument(
        "--exclude-file",
        metavar="FILE",
        help="File containing exclusion patterns (one per line). "
             "Not allowed when target is a file."
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    try:
        return lineblock(
            path=args.path,
            pattern=args.patterns,
            exclude=args.excludes,
            exclude_file=args.exclude_file,
            dirs=args.dirs
        )

    except (
            OrphanedInsertEndMarkerError,
            OrphanedExtractEndMarkerError,
            UnclosedBlockError,
            FileNotFoundError,
            NotADirectoryError,
            NotAFileError,
            IncompatibleOptionsError
    ) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        print("Traceback (most recent call last):", file=sys.stderr)
        traceback.print_exception(type(e), e, e.__traceback__)
        return 1


if __name__ == "__main__":
    sys.exit(main())