"""
CLI entry point for the lineblock package.
"""

from lineblock.block_extract import BlockExtract
from lineblock.block_insert import BlockInsert
from lineblock.exceptions import UnclosedBlockError, OrphanedExtractEndMarkerError
import argparse


def lineblocks(action: str,
               source: str = None,
               prefix: str = None,
               output: str = None,
               clear: bool = False):
    """
    Combined function for inserting or extracting code blocks.
    """

    # Validate action
    if action not in ("insert", "extract"):
        raise ValueError(f'action must be "insert" or "extract", got "{action}"')

    try:
        if action == "insert":
            # Validate parameters for insert
            if not all([source, prefix]):
                raise ValueError('source and prefix must be specified for insert action')

            # Call insert function
            BlockInsert.process_path(source, prefix, output, clear)

        else:  # action == "extract"
            # Validate parameters for extract
            if not all([source, prefix]):
                raise ValueError('source and prefix must be specified for extract action')
            if any([output, clear]):
                raise ValueError(
                    'output and clear should not be specified for extract action')

            # Call extract function
            extractor = BlockExtract()
            extractor.process_path(source, prefix)

    except (FileNotFoundError, NotADirectoryError, ValueError) as e:
        # Handle common file/directory and parameter validation errors
        print(f"Error: {e}")
        raise
    except (UnclosedBlockError, OrphanedExtractEndMarkerError) as e:
        # Handle extraction-specific errors
        print(f"Error: {e}")
        raise
    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Insert or extract code blocks based on markers in Python/Markdown files."
    )

    # Create subparsers for different actions
    subparsers = parser.add_subparsers(dest='action', help='Available actions', required=True)

    # Extract subparser
    extract_parser = subparsers.add_parser('extract', help='Extract code blocks from source files')
    extract_parser.add_argument(
        "--source",
        required=True,
        help="Source file to process."
    )
    extract_parser.add_argument(
        "--prefix",
        default=".",  # Set default prefix to "."
        help="Base path for block files (default: '.')."
    )

    # Insert subparser
    insert_parser = subparsers.add_parser('insert', help='Insert code blocks into source files')
    insert_parser.add_argument(
        "--source",
        required=True,
        help="Source file to process."
    )
    insert_parser.add_argument(
        "--prefix",
        default=".",  # Set default prefix to "."
        help="Base path for block files (default: '.')."
    )
    insert_parser.add_argument(
        "--output",
        help="Directory for generated files (preserves structure). If omitted, modifies sources in-place."
    )
    insert_parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear blocks without insertion (insert action only)."
    )

    args = parser.parse_args()

    try:
        # Call the unified function
        lineblocks(
            action=args.action,
            source=args.source,
            prefix=args.prefix,
            output=getattr(args, 'output', None),
            clear=getattr(args, 'clear', False)
        )
    except (UnclosedBlockError, OrphanedExtractEndMarkerError,
            FileNotFoundError, NotADirectoryError, ValueError) as e:
        # Exit with non-zero status to indicate error
        exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        exit(1)

    return 0