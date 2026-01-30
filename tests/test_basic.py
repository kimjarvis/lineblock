# test_example.py
import logging
import os

from block_insert import block_insert

logger = logging.getLogger(__name__)


def test_last_line():
    # Call the function that generates the output file
    print("hello world")
    block_insert(
        source_path="tests/sources/last_line.md",
        insert_path="tests/snippets",
        output_path="tests/outputs"
    )

    # Define paths to the generated and expected files
    output_file = "tests/outputs/last_line.md"
    expected_file = "tests/expected/last_line.md"

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


def test_basic_md():
    # Call the function that generates the output file
    print("hello world")
    block_insert(
        source_path="tests/sources/basic.md",
        insert_path="tests/snippets",
        output_path="tests/outputs"
    )

    # Define paths to the generated and expected files
    output_file = "tests/outputs/basic.md"
    expected_file = "tests/expected/basic.md"

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


def test_basic_py():
    # Call the function that generates the output file
    print("hello world")
    block_insert(
        source_path="tests/sources/basic.py",
        insert_path="tests/snippets",
        output_path="tests/outputs"
    )

    # Define paths to the generated and expected files
    output_file = "tests/outputs/basic.py"
    expected_file = "tests/expected/basic.py"

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


def test_not_found():
    # Call the function that generates the output file
    print("hello world")
    block_insert(
        source_path="tests/sources/not_found.md",
        insert_path="tests/snippets",
        output_path="tests/outputs"
    )

    # Define paths to the generated and expected files
    output_file = "tests/outputs/not_found.md"
    expected_file = "tests/expected/not_found.md"

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

def test_not_found1():
    # Call the function that generates the output file
    print("hello world")
    block_insert(
        source_path="tests/sources/not_found1.md",
        insert_path="tests/snippets",
        output_path="tests/outputs"
    )

    # Define paths to the generated and expected files
    output_file = "tests/outputs/not_found1.md"
    expected_file = "tests/expected/not_found1.md"

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


def test_done_already():
    # Call the function that generates the output file
    print("hello world")
    block_insert(
        source_path="tests/sources/done_already.md",
        insert_path="tests/snippets",
        output_path="tests/outputs"
    )

    # Define paths to the generated and expected files
    output_file = "tests/outputs/done_already.md"
    expected_file = "tests/expected/done_already.md"

    assert not os.path.exists(output_file), f"Output file not found: {output_file}"

