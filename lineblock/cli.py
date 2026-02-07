"""
CLI entry point for the lineblock package.
"""

from lineblock.block_extract import BlockExtract, block_extract
from lineblock.block_insert import BlockInsert, block_insert
from lineblock.exceptions import UnclosedBlockError, OrphanedExtractEndMarkerError
import argparse


def lineblock(action: str,
               source: str = None,
               prefix: str = None,
               output: str = None,
               clear: bool = False,
               extract_begin_prefix: str = None,
               extract_begin_suffix: str = None,
               extract_end_prefix: str = None,
               extract_end_suffix: str = None,
               insert_begin_prefix: str = None,
               insert_begin_suffix: str = None,
               insert_end_prefix: str = None,
               insert_end_suffix: str = None,
               ):
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
            block_insert(
                source_file=source,
                insert_directory_prefix=prefix,
                output_directory=output,
                clear_mode=clear,
                insert_begin_prefix=insert_begin_prefix,
                insert_begin_suffix=insert_begin_suffix,
                insert_end_prefix=insert_end_prefix,
                insert_end_suffix=insert_end_suffix,
            )

        else:  # action == "extract"
            # Validate parameters for extract
            if not all([source, prefix]):
                raise ValueError('source and prefix must be specified for extract action')
            if any([output, clear]):
                raise ValueError('output and clear parameters are not valid for extract action')

            # Call extract function
            block_extract(
                source_path=source,
                extract_directory_prefix=prefix,
                extract_begin_prefix=extract_begin_prefix,
                extract_begin_suffix=extract_begin_suffix,
                extract_end_prefix=extract_end_prefix,
                extract_end_suffix=extract_end_suffix
            )

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
    extract_parser.add_argument(
        "--extract_begin_prefix",
        default=r"#\s*block extract\s+",
        help="Regex prefix for extract begin marker (default: '#\\s*block extract\\s+')"
    )
    extract_parser.add_argument(
        "--extract_begin_suffix",
        default=r"",
        help="Regex suffix for extract begin marker (default: '')"
    )
    extract_parser.add_argument(
        "--extract_end_prefix",
        default=r"#\s*end extract\s+",
        help="Regex prefix for extract end marker (default: '#\\s*end extract\\s+')"
    )
    extract_parser.add_argument(
        "--extract_end_suffix",
        default=r"",
        help="Regex suffix for extract end marker (default: '')"
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
    insert_parser.add_argument(
        "--insert_begin_prefix",
        default=r"<!--\s*block insert\s+",
        help="Regex prefix for insert begin marker (default: '<!--\\s*block insert\\s+')"
    )
    insert_parser.add_argument(
        "--insert_begin_suffix",
        default=r"\s*-->",
        help="Regex suffix for insert begin marker (default: '\\s*-->')"
    )
    insert_parser.add_argument(
        "--insert_end_prefix",
        default=r"<!--\s*end insert",
        help="Regex prefix for insert end marker (default: '<!--\\s*end insert')"
    )
    insert_parser.add_argument(
        "--insert_end_suffix",
        default=r"\s*-->",
        help="Regex suffix for insert end marker (default: '\\s*-->')"
    )

    args = parser.parse_args()

    try:
        # Call the unified function
        lineblock(
            action=args.action,
            source=args.source,
            prefix=args.prefix,
            output=getattr(args, 'output', None),
            clear=getattr(args, 'clear', False),
            extract_begin_prefix=getattr(args, 'extract_begin_prefix', None),
            extract_begin_suffix=getattr(args, 'extract_begin_suffix', None),
            extract_end_prefix=getattr(args, 'extract_end_prefix', None),
            extract_end_suffix=getattr(args, 'extract_end_suffix', None),
            insert_begin_prefix=getattr(args, 'insert_begin_prefix', None),
            insert_begin_suffix=getattr(args, 'insert_begin_suffix', None),
            insert_end_prefix=getattr(args, 'insert_end_prefix', None),
            insert_end_suffix=getattr(args, 'insert_end_suffix', None),
        )
    except (UnclosedBlockError, OrphanedExtractEndMarkerError,
            FileNotFoundError, NotADirectoryError, ValueError) as e:
        # Exit with non-zero status to indicate error
        exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        exit(1)

    return 0