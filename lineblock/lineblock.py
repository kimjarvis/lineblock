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


from lineblock.exceptions import OrphanedExtractEndMarkerError, UnclosedBlockError, NotAFileError, IncompatibleOptionsError
from lineblock.process import process, process_inserts




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


def traverse_directory1(
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
                block_map.extend(process(file_path=path.resolve()))

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


def handle_single_file1(target_path: Path) -> None:
    """
    Handle case when positional argument is a single file.
    Prints the absolute path of the file.
    """
    if not target_path.exists():
        raise FileNotFoundError(f"File does not exist: {target_path}")

    if not target_path.is_file():
        raise NotAFileError(f"Not a file: {target_path}")

    block_map = []
    block_map.extend(process(file_path=target_path.resolve())) # todo: what to do here?
    print(block_map)
    process_inserts(block_map=block_map, file_path=target_path.resolve())
    return



def parse_args():
    """Placeholder for argument parsing - returns argparse.Namespace."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Target path")
    parser.add_argument("-p", "--patterns", nargs="*", default=None)
    parser.add_argument("-x", "--excludes", nargs="*", default=None)
    parser.add_argument("--exclude-file", default=None)
    parser.add_argument("-d", "--dirs", nargs="*", default=None)
    return parser.parse_args()


def load_exclude_patterns(exclude_file: str) -> List[str]:
    """Load exclusion patterns from a file."""
    patterns = []
    with open(exclude_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                patterns.append(line)
    return patterns


def handle_single_file(target_path: Path) -> None:
    """Process a single file."""
    # Implementation placeholder
    print(f"Processing single file: {target_path}")
    handle_single_file1(target_path=target_path)


def traverse_directory(
        root: Path,
        patterns: Optional[List[str]] = None,
        subdirs: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
) -> None:
    """Traverse directory with given patterns."""
    # Implementation placeholder
    print(f"Traversing directory: {root}")
    if patterns:
        print(f"  Patterns: {patterns}")
    if subdirs:
        print(f"  Subdirs: {subdirs}")
    if exclude_patterns:
        print(f"  Excludes: {exclude_patterns}")
    traverse_directory1(root=root, patterns=patterns, subdirs=subdirs, exclude_patterns=exclude_patterns)

def lineblock(
        path: Union[str, Path],
        pattern: Optional[Union[str, List[str]]] = None,
        exclude: Optional[Union[str, List[str]]] = None,
        exclude_file: Optional[str] = None,
        dirs: Optional[Union[str, List[str]]] = None
) -> int:
    """
    Process files with line blocking logic.

    Args:
        path: Target path (file or directory)
        pattern: Pattern(s) to match (directory only)
        exclude: Pattern(s) to exclude (directory only)
        exclude_file: File containing exclusion patterns (directory only)
        dirs: Specific subdirectories to process (directory only)

    Returns:
        0 on success, 1 on error

    Raises:
        IncompatibleOptionsError: If incompatible options provided for file target
        FileNotFoundError: If path does not exist
        NotADirectoryError: If directory expected but not found
        NotAFileError: If file expected but not found
    """
    # Resolve target path (expand user and make absolute)
    target_path = Path(path).expanduser().resolve()

    # Normalize list inputs
    patterns = _normalize_to_list(pattern)
    excludes = _normalize_to_list(exclude)
    subdirs = _normalize_to_list(dirs)

    # Verify path exists
    if not target_path.exists():
        raise FileNotFoundError(f"Path does not exist: {target_path}")

    # Determine if target is a file or directory
    is_file_target = target_path.is_file()

    # Validate incompatible options when target is a file
    if is_file_target:
        incompatible_options = []
        if patterns is not None:
            incompatible_options.append("pattern")
        if excludes is not None:
            incompatible_options.append("exclude")
        if exclude_file is not None:
            incompatible_options.append("exclude_file")
        if subdirs is not None:
            incompatible_options.append("dirs")

        if incompatible_options:
            raise IncompatibleOptionsError(
                f"Options {', '.join(incompatible_options)} not allowed when target is a file"
            )

    if is_file_target:
        handle_single_file(target_path)
    else:
        # Treat as directory traversal
        if not target_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {target_path}")

        # Collect exclusion patterns
        exclude_patterns = list(excludes) if excludes else []
        if exclude_file:
            exclude_patterns.extend(load_exclude_patterns(exclude_file))

        traverse_directory(
            root=target_path,
            patterns=patterns,
            subdirs=subdirs,
            exclude_patterns=exclude_patterns
        )

    return 0


def _normalize_to_list(value: Optional[Union[str, List[str]]]) -> Optional[List[str]]:
    """Normalize string or list input to list, or None if empty/None."""
    if value is None:
        return None
    if isinstance(value, str):
        return [value] if value else None
    return list(value) if value else None


