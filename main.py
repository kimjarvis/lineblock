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
from typing import List, Optional


from lineblock.exceptions import OrphanedExtractEndMarkerError, UnclosedBlockError
from lineblock.process import process, process_inserts

class NotAFileError(Exception):
    """Raised when a file operation expects a file but gets something else."""
    pass


class IncompatibleOptionsError(ValueError):
    """Raised when incompatible options are used together."""
    pass


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


def load_exclude_patterns(exclude_file: Optional[str]) -> List[str]:
    """Load exclusion patterns from a file."""
    patterns = []
    if exclude_file and os.path.exists(exclude_file):
        with open(exclude_file, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns


def should_exclude(path: Path, exclude_patterns: List[str], root: Path) -> bool:
    """
    Check if path should be excluded based on gitignore-style patterns.
    Supports:
    - simple name (e.g., "node_modules")
    - glob patterns (e.g., "*.pyc", "temp.*")
    - directory patterns (e.g., "build/", "*.egg-info/")
    - path patterns (e.g., "docs/_build")
    """
    # Get path relative to root for matching
    try:
        rel_path = path.relative_to(root)
    except ValueError:
        rel_path = path

    rel_str = str(rel_path).replace(os.sep, '/')
    path_parts = rel_str.split('/')

    for pattern in exclude_patterns:
        pattern = pattern.rstrip()
        if not pattern:
            continue

        # Handle directory-specific patterns (trailing /)
        is_dir_pattern = pattern.endswith('/')
        if is_dir_pattern:
            pattern = pattern[:-1]
            if not path.is_dir():
                continue

        # Check if pattern matches any component or the full path
        if pattern in path_parts:
            return True

        # Check glob match against full relative path
        if fnmatch.fnmatch(rel_str, pattern):
            return True

        # Check glob match against file/directory name
        if fnmatch.fnmatch(path.name, pattern):
            return True

        # Check if pattern matches any parent directory component
        for i, part in enumerate(path_parts):
            partial_path = '/'.join(path_parts[:i + 1])
            if fnmatch.fnmatch(partial_path, pattern):
                return True

    return False


def get_target_dirs(root: Path, subdirs: Optional[List[str]]) -> List[Path]:
    """Get list of directories to traverse."""
    if subdirs is None:
        return [root]

    targets = []
    for subdir in subdirs:
        target = root / subdir
        if target.exists() and target.is_dir():
            targets.append(target)
        else:
            raise FileNotFoundError(f"Sub-directory not found: {target}")

    return targets if targets else [root]


def matches_patterns(path: Path, patterns: Optional[List[str]]) -> bool:
    """Check if file matches the specified patterns."""
    if patterns is None:
        return True

    return any(fnmatch.fnmatch(path.name, p) for p in patterns)


def traverse_directory(
        root: Path,
        patterns: Optional[List[str]],
        subdirs: Optional[List[str]],
        exclude_patterns: List[str]
) -> None:
    """
    Traverse directory and print matching file absolute paths.
    """
    target_dirs = get_target_dirs(root, subdirs)

    block_map = []
    for start_dir in target_dirs:
        if not start_dir.exists():
            raise FileNotFoundError(f"Directory does not exist: {start_dir}")

        if not start_dir.is_dir():
            raise NotADirectoryError(f"Not a directory: {start_dir}")

        # Use rglob for recursive traversal
        for path in start_dir.rglob('*'):
            # Skip if excluded
            if should_exclude(path, exclude_patterns, root):
                continue

            # Skip directories (we only print files)
            if not path.is_file():
                continue

            # Check pattern match
            if matches_patterns(path, patterns):
                block_map.extend(process(root_path=root,file_path=path.resolve()))

        # Again for insert
    for start_dir in target_dirs:
        # Use rglob for recursive traversal
        for path in start_dir.rglob('*'):
            # Skip if excluded
            if should_exclude(path, exclude_patterns, root):
                continue

            # Skip directories (we only print files)
            if not path.is_file():
                continue

            # Check pattern match
            if matches_patterns(path, patterns):
                process_inserts(block_map=block_map, file_path=path.resolve())
    return


def handle_single_file(target_path: Path) -> None:
    """
    Handle case when positional argument is a single file.
    Prints the absolute path of the file.
    """
    if not target_path.exists():
        raise FileNotFoundError(f"File does not exist: {target_path}")

    if not target_path.is_file():
        raise NotAFileError(f"Not a file: {target_path}")

    block_map = []
    block_map.append(process(root_path=target_path.parent(),file_path=target_path.resolve())) # todo: what to do here?
    print(block_map)
    process_inserts(block_map=block_map, file_path=target_path.resolve())
    return


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Resolve target path (expand user and make absolute)
    target_path = Path(args.path).expanduser().resolve()

    # Determine if target is a file or directory
    is_file_target = False

    if target_path.exists():
        is_file_target = target_path.is_file()

    # Validate incompatible options when target is a file
    if is_file_target:
        incompatible_options = []
        if args.patterns is not None:
            incompatible_options.append("-p/--pattern")
        if args.excludes is not None:
            incompatible_options.append("-x/--exclude")
        if args.exclude_file is not None:
            incompatible_options.append("--exclude-file")
        if args.dirs is not None:
            incompatible_options.append("-d/--dirs")

        if incompatible_options:
            raise IncompatibleOptionsError(
                f"Options {', '.join(incompatible_options)} not allowed when target is a file"
            )

    try:
        if is_file_target:
            handle_single_file(target_path)
        else:
            # Treat as directory traversal
            if not target_path.exists():
                raise FileNotFoundError(f"Path does not exist: {target_path}")

            if not target_path.is_dir():
                raise NotADirectoryError(f"Not a directory: {target_path}")

            # Collect exclusion patterns
            exclude_patterns = args.excludes or []
            if args.exclude_file:
                exclude_patterns.extend(load_exclude_patterns(args.exclude_file))

            traverse_directory(
                root=target_path,
                patterns=args.patterns,
                subdirs=args.dirs,
                exclude_patterns=exclude_patterns
            )

        return 0

    except (
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