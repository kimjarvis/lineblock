import argparse
from lineblock.block_extract import BlockExtract
from lineblock.block_insert import BlockInsert
from lineblock.exceptions import UnclosedBlockError, OrphanedExtractEndMarkerError


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

    # Positional action argument
    parser.add_argument(
        "action",
        choices=["insert", "extract"],
        help="Action to perform: 'insert' to insert code blocks, 'extract' to extract them."
    )

    # Common arguments group
    common_group = parser.add_argument_group('Common arguments')
    common_group.add_argument(
        "--source",
        required=True,
        help="Source file to process."
    )
    common_group.add_argument(
        "--prefix",
        required=True,
        help="Base path for block files (required for both actions)."
    )

    # Insert-specific arguments group
    insert_group = parser.add_argument_group('Insert-specific arguments')
    insert_group.add_argument(
        "--output",
        help="Directory for generated files (preserves structure). If omitted, modifies sources in-place."
    )
    insert_group.add_argument(
        "--clear",
        action="store_true",
        help="Clear blocks without insertion (insert action only)."
    )

    args = parser.parse_args()

    # Validate action-specific arguments
    if args.action == "extract":
        if args.output or args.clear:
            parser.error("--output and --clear should not be specified for extract action")

    try:
        # Call the unified function
        lineblocks(
            action=args.action,
            source=args.source,
            prefix=args.prefix,
            output=args.output,
            clear=args.clear
        )
    except (UnclosedBlockError, OrphanedExtractEndMarkerError,
            FileNotFoundError, NotADirectoryError, ValueError) as e:
        # Exit with non-zero status to indicate error
        exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        exit(1)

    return 0


if __name__ == "__main__":
    main()