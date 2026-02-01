# test_example.py
import logging
import os
import pytest
from lineblocks.block_insert import block_insert, OrphanedInsertEndMarkerError
from lineblocks.block_extract import block_extract, UnclosedBlockError, OrphanedExtractEndMarkerError


logger = logging.getLogger(__name__)


def run_and_compare_file_test(func, source_filename, test_type="insert"):
    """Helper function to run a test and compare output with expected file."""
    # Remove file extension to get base name
    base_name = os.path.splitext(source_filename)[0]

    # Determine function to call and paths based on test type
    if test_type == "insert":
        func(
            source_file=f"tests/sources/{source_filename}",
            insert_directory_prefix="tests/snippets",
            output_directory="tests/outputs"
        )
        output_file = f"tests/outputs/{base_name}.md"
    else:  # extract
        func(
            source_path=f"tests/sources/{source_filename}",
            extract_directory_prefix="tests/outputs",
        )
        output_file = f"tests/outputs/{base_name}.md"

    expected_file = f"tests/expected/{base_name}.md"

    # Assert that both files exist
    assert os.path.exists(output_file), f"Output file not found: {output_file}"
    assert os.path.exists(expected_file), f"Expected file not found: {expected_file}"

    # Read the contents of both files
    with open(output_file, "r", encoding="utf-8") as f:
        output_content = f.read()
    with open(expected_file, "r", encoding="utf-8") as f:
        expected_content = f.read()

    # Assert that the contents are identical
    assert output_content == expected_content, "Generated file content does not match expected content."


# Parameterized insert tests
@pytest.mark.parametrize("source_file", [
    "last_line.md",
    "basic.md",
    "basic.py",
    "not_found.md",
    "not_found1.md",
    "indent_1.md",
    "indent_2.md",
    "indent_3.md"
])
def test_insert_files(source_file):
    """Test various insert operations."""
    run_and_compare_file_test(block_insert, source_file, test_type="insert")


# Parameterized extract tests
@pytest.mark.parametrize("source_file", [
    "basic_extract.md",
    "extract_last_line.md",
    "extract_indent_1.md",
    "extract_indent_2.md",
])
def test_extract_files(source_file):
    """Test various extract operations."""
    run_and_compare_file_test(block_extract, source_file, test_type="extract")


def test_done_already():
    """Special test - do not modify this test."""
    # Call the function that generates the output file
    block_insert(
        source_file="tests/sources/done_already.md",
        insert_directory_prefix="tests/snippets",
        output_directory="tests/outputs"
    )

    # Define paths to the generated and expected files
    output_file = "tests/outputs/done_already.md"

    assert not os.path.exists(output_file), f"Output file not found: {output_file}"

def test_insert_orphaned_end_marker():
    """Test when a block end marker appears before any block extract marker."""
    source_path = "tests/sources/insert_orphaned_end_marker.md"

    with pytest.raises(OrphanedInsertEndMarkerError) as exc_info:
        block_extract(
            source_path="tests/sources/insert_orphaned_end_marker.md",
            extract_directory_prefix="tests/snippets"
        )

    assert "Orphaned block end marker" in str(exc_info.value)
    assert "insert_orphaned_end_marker.md" in str(exc_info.value)
    # Should mention line 2 (since line numbers are 1-based)
    assert "line 2" in str(exc_info.value) or "at line" in str(exc_info.value)



def test_unclosed_block():
    """Test that an UnclosedBlockError is raised when a block has no end marker."""
    # Using pytest.raises to assert that the exception is raised
    with pytest.raises(UnclosedBlockError) as exc_info:
        block_extract(
            source_path="tests/sources/extract_missing_end.md",
            extract_directory_prefix="tests/snippets"
        )

    # Optional: Verify exception details
    assert exc_info.value.line_number == 2  # Assuming the block starts on line 2
    assert "Unclosed block" in str(exc_info.value)


def test_extract_orphaned_end_marker():
    """Test when a block end marker appears before any block extract marker."""
    source_path = "tests/sources/extract_orphaned_end_marker.md"

    with pytest.raises(OrphanedExtractEndMarkerError) as exc_info:
        block_extract(
            source_path="tests/sources/extract_orphaned_end_marker.md",
            extract_directory_prefix="tests/snippets"
        )

    assert "Orphaned block end marker" in str(exc_info.value)
    assert "extract_orphaned_end_marker.md" in str(exc_info.value)
    # Should mention line 2 (since line numbers are 1-based)
    assert "line 2" in str(exc_info.value) or "at line" in str(exc_info.value)


def test_extract_orphaned_begin_marker():
    """Test when a block extract marker has no corresponding end marker."""
    source_path = "tests/sources/extract_orphaned_begin_marker.md"

    with pytest.raises(UnclosedBlockError) as exc_info:
        block_extract(
            source_path="tests/sources/extract_orphaned_begin_marker.md",
            extract_directory_prefix="tests/snippets"
        )

    assert "Unclosed block" in str(exc_info.value)
    assert "extract_orphaned_begin_marker.md" in str(exc_info.value)
    assert "Expected end marker" in str(exc_info.value)


def test_extract_nested_markers():
    """Test when a block extract marker appears inside another block (nested)."""
    source_path = "tests/sources/extract_nested_markers.md"

    with pytest.raises(OrphanedExtractEndMarkerError) as exc_info:
        block_extract(
            source_path="tests/sources/extract_nested_markers.md",
            extract_directory_prefix="tests/snippets"
        )

    # Verify error message contains expected information
    assert "Orphaned block end marker" in str(exc_info.value)
    assert "extract_nested_markers.md" in str(exc_info.value)
    # The error should occur at the second block extract marker (line 3)
    assert "line 3" in str(exc_info.value) or "at line" in str(exc_info.value)
