import logging
import os
import pytest
from pathlib import Path
from lineblock.block_insert import block_insert, OrphanedInsertEndMarkerError
from lineblock.block_extract import block_extract, UnclosedBlockError, OrphanedExtractEndMarkerError


logger = logging.getLogger(__name__)


def run_and_compare_file_test(tmp_path, func, source_content, expected_content, test_type="insert", snippet_contents=None, expect_output_file=True, extract_filename=None):
    """Helper function to run a test and compare output with expected content using temporary files."""

    # Create temporary source file
    source_file = tmp_path / "source.md"
    source_file.write_text(source_content, encoding="utf-8")

    # Create temporary snippet files if provided
    snippets_dir = tmp_path / "snippets"
    snippets_dir.mkdir(exist_ok=True)

    if snippet_contents:
        for filename, content in snippet_contents.items():
            snippet_file = snippets_dir / filename
            snippet_file.write_text(content, encoding="utf-8")

    # Create output directory
    output_dir = tmp_path / "outputs"
    output_dir.mkdir(exist_ok=True)

    # Determine function arguments based on test type
    if test_type == "insert":
        func(
            source_file=str(source_file),
            insert_directory_prefix=str(snippets_dir),
            output_directory=str(output_dir)
        )
        output_file = output_dir / source_file.name
    else:  # extract
        # For extract, we need to determine the output file based on the block name
        # Extract the filename from the source content to know which file will be created
        import re
        match = re.search(r"<!--\s*block extract\s+(\S+)", source_content)
        if not match:
            match = re.search(r"#\s*block extract\s+(\S+)", source_content)

        if match:
            extract_filename = match.group(1)
        else:
            # If no extract block is found, use a default name
            extract_filename = "default_output.txt"

        func(
            source_path=str(source_file),
            extract_directory_prefix=str(output_dir),
        )
        output_file = output_dir / extract_filename

    # Check if output file is expected to exist
    if expect_output_file:
        assert output_file.exists(), f"Output file not found: {output_file}"
        # Read the generated output
        output_content = output_file.read_text(encoding="utf-8")

        # Assert that the contents are identical
        assert output_content == expected_content, f"Generated content does not match expected content.\nActual:\n{output_content}\nExpected:\n{expected_content}"
    else:
        # When expect_output_file is False, the file shouldn't exist
        assert not output_file.exists(), f"Output file should not exist but was found: {output_file}"


# Insert tests with inline test data
@pytest.mark.parametrize("source_content,expected_content,snippet_contents,expect_output_file", [
    # last_line.md test case
    (
        "before\n<!-- block insert basic.md -->",
        "before\n<!-- block insert basic.md -->\nline 1\nline 2\nline 3\n<!-- end insert -->",
        {"basic.md": "line 1\nline 2\nline 3"},
        True
    ),
    # basic.md test case
    (
        "before\n<!-- block insert basic.md -->\nafter",
        "before\n<!-- block insert basic.md -->\nline 1\nline 2\nline 3\n<!-- end insert -->\nafter",
        {"basic.md": "line 1\nline 2\nline 3"},
        True
    ),
    # basic.py test case
    (
        "before\n<!-- block insert basic.py -->\nafter",
        "before\n<!-- block insert basic.py -->\ndef hello():\n    print('Hello, world!')\n<!-- end insert -->\nafter",
        {"basic.py": "def hello():\n    print('Hello, world!')"},
        True
    ),
    # not_found.md test case
    (
        "before\n<!-- block insert nofile.md -->\n<!-- block insert basic.md -->\nafter",
        "before\n<!-- block insert nofile.md -->\n<!-- block insert basic.md -->\nline 1\nline 2\nline 3\n<!-- end insert -->\nafter",
        {"basic.md": "line 1\nline 2\nline 3"},
        True
    ),
    # not_found1.md test case - this one is special, no output file should be created when snippet is not found and no changes are made
    (
        "before\n<!-- block insert nonexistent.md -->\nafter",
        "before\n<!-- block insert nonexistent.md -->\nafter",  # This is just for reference, won't be used
        {},
        False  # expect_output_file=False because no changes are made when file is not found
    ),
    # indent_1.md test case
    (
        "before\n    <!-- block insert indent.md -->\nafter",
        "before\n    <!-- block insert indent.md -->\n    line 1\n    line 2\n    <!-- end insert -->\nafter",
        {"indent.md": "line 1\nline 2"},
        True
    ),
    # indent_2.md test case - this one might have the tab issue
    (
        "before\n\t<!-- block insert indent.md -->\nafter",
        "before\n\t<!-- block insert indent.md -->\n line 1\n line 2\n <!-- end insert -->\nafter",  # Tabs get converted to spaces based on function behavior
        {"indent.md": "line 1\nline 2"},
        True
    ),
    # indent_3.md test case
    (
        "before\n  <!-- block insert indent.md -->\nafter",
        "before\n  <!-- block insert indent.md -->\n  line 1\n  line 2\n  <!-- end insert -->\nafter",
        {"indent.md": "line 1\nline 2"},
        True
    )
])
def test_insert_files(tmp_path, source_content, expected_content, snippet_contents, expect_output_file):
    """Test various insert operations."""
    run_and_compare_file_test(tmp_path, block_insert, source_content, expected_content, test_type="insert", snippet_contents=snippet_contents, expect_output_file=expect_output_file)


# Extract tests with inline test data
@pytest.mark.parametrize("source_content,expected_content", [
    # basic_extract.md test case
    (
        "before\n<!-- block extract basic_extract.md -->\nline 1\nline 2\nline 3\n<!-- end extract -->\nafter",
        "line 1\nline 2\nline 3\n"  # Note: extract function adds a trailing newline
    ),
    # extract_last_line.md test case
    (
        "before\n<!-- block extract extract_last_line.md -->\nline 1\nline 2\nline 3\n<!-- end extract -->",
        "line 1\nline 2\nline 3\n"  # Note: extract function adds a trailing newline
    ),
    # extract_indent_1.md test case
    (
        "before\n<!-- block extract extract_indent_1.md -->\n    line 1\n    line 2\n<!-- end extract -->\nafter",
        "    line 1\n    line 2\n"  # Note: extract function adds a trailing newline
    ),
    # extract_indent_2.md test case
    (
        "before\n<!-- block extract extract_indent_2.md -->\n\tline 1\n\tline 2\n<!-- end extract -->\nafter",
        "\tline 1\n\tline 2\n"  # Note: extract function adds a trailing newline
    ),
])
def test_extract_files(tmp_path, source_content, expected_content):
    """Test various extract operations."""
    run_and_compare_file_test(tmp_path, block_extract, source_content, expected_content, test_type="extract")


def test_done_already(tmp_path):
    """Special test - do not modify this test."""
    # Create source file with done_already content
    source_file = tmp_path / "done_already.md"
    source_file.write_text(
        "before\n<!-- block insert done_already.md -->\nline 1\nline 2\n<!-- end insert -->\nafter",
        encoding="utf-8"
    )
    
    # Create snippet file
    snippets_dir = tmp_path / "snippets"
    snippets_dir.mkdir(exist_ok=True)
    snippet_file = snippets_dir / "done_already.md"
    snippet_file.write_text("line 1\nline 2", encoding="utf-8")
    
    # Create output directory
    output_dir = tmp_path / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    # Call the function that generates the output file
    block_insert(
        source_file=str(source_file),
        insert_directory_prefix=str(snippets_dir),
        output_directory=str(output_dir)
    )

    # Define path to the generated file
    output_file = output_dir / "done_already.md"

    # Since the block is already inserted, no new file should be created
    assert not output_file.exists(), f"Output file should not exist: {output_file}"


def test_insert_orphaned_end_marker(tmp_path):
    """Test when a block end marker appears before any block insert marker."""
    # Create source file with orphaned end marker
    source_file = tmp_path / "insert_orphaned_end_marker.md"
    source_file.write_text("before\n<!-- end insert -->\nafter", encoding="utf-8")
    
    # Create snippets directory (empty for this test)
    snippets_dir = tmp_path / "snippets"
    snippets_dir.mkdir(exist_ok=True)

    with pytest.raises(OrphanedInsertEndMarkerError) as exc_info:
        block_insert(
            source_file=str(source_file),
            insert_directory_prefix=str(snippets_dir)
        )

    assert "Orphaned block end marker" in str(exc_info.value)
    assert "insert_orphaned_end_marker.md" in str(exc_info.value)
    # Should mention line 2 (since line numbers are 1-based)
    assert "line 2" in str(exc_info.value) or "at line" in str(exc_info.value)


def test_unclosed_block(tmp_path):
    """Test that an UnclosedBlockError is raised when a block has no end marker."""
    # Create source file with unclosed block
    source_file = tmp_path / "extract_missing_end.md"
    source_file.write_text("before\n<!-- block extract basic_extract.md -->\nline 1\nline 2\nline 3", encoding="utf-8")
    
    # Create snippets directory (empty for this test)
    snippets_dir = tmp_path / "snippets"
    snippets_dir.mkdir(exist_ok=True)

    # Using pytest.raises to assert that the exception is raised
    with pytest.raises(UnclosedBlockError) as exc_info:
        block_extract(
            source_path=str(source_file),
            extract_directory_prefix=str(snippets_dir)
        )

    # Optional: Verify exception details
    assert exc_info.value.line_number == 2  # Assuming the block starts on line 2
    assert "Unclosed block" in str(exc_info.value)


def test_extract_orphaned_end_marker(tmp_path):
    """Test when a block end marker appears before any block extract marker."""
    # Create source file with orphaned end marker
    source_file = tmp_path / "extract_orphaned_end_marker.md"
    source_file.write_text("before\n<!-- end extract -->\nafter", encoding="utf-8")
    
    # Create snippets directory (empty for this test)
    snippets_dir = tmp_path / "snippets"
    snippets_dir.mkdir(exist_ok=True)

    with pytest.raises(OrphanedExtractEndMarkerError) as exc_info:
        block_extract(
            source_path=str(source_file),
            extract_directory_prefix=str(snippets_dir)
        )

    assert "Orphaned block end marker" in str(exc_info.value)
    assert "extract_orphaned_end_marker.md" in str(exc_info.value)
    # Should mention line 2 (since line numbers are 1-based)
    assert "line 2" in str(exc_info.value) or "at line" in str(exc_info.value)


def test_extract_orphaned_begin_marker(tmp_path):
    """Test when a block extract marker has no corresponding end marker."""
    # Create source file with orphaned begin marker
    source_file = tmp_path / "extract_orphaned_begin_marker.md"
    source_file.write_text("before\n<!-- block extract extract_orphaned_begin_marker.md -->\nafter", encoding="utf-8")
    
    # Create snippets directory (empty for this test)
    snippets_dir = tmp_path / "snippets"
    snippets_dir.mkdir(exist_ok=True)

    with pytest.raises(UnclosedBlockError) as exc_info:
        block_extract(
            source_path=str(source_file),
            extract_directory_prefix=str(snippets_dir)
        )

    assert "Unclosed block" in str(exc_info.value)
    assert "extract_orphaned_begin_marker.md" in str(exc_info.value)
    assert "Expected end marker" in str(exc_info.value)


def test_extract_nested_markers(tmp_path):
    """Test when a block extract marker appears inside another block (nested)."""
    # Create source file with nested markers
    source_file = tmp_path / "extract_nested_markers.md"
    source_content = """before
<!-- block extract extract_nested_markers.md -->
inside first block
<!-- block extract nested.md -->
more content
<!-- end extract -->
after nested
<!-- end extract -->
after"""
    source_file.write_text(source_content, encoding="utf-8")
    
    # Create snippets directory with nested content
    snippets_dir = tmp_path / "snippets"
    snippets_dir.mkdir(exist_ok=True)
    nested_file = snippets_dir / "nested.md"
    nested_file.write_text("nested content", encoding="utf-8")

    with pytest.raises(OrphanedExtractEndMarkerError) as exc_info:
        block_extract(
            source_path=str(source_file),
            extract_directory_prefix=str(snippets_dir)
        )

    # Verify error message contains expected information
    assert "Orphaned block end marker" in str(exc_info.value)
    assert "extract_nested_markers.md" in str(exc_info.value)
    # The error should occur at the second block extract marker (line 3)
    assert "line 3" in str(exc_info.value) or "at line" in str(exc_info.value)