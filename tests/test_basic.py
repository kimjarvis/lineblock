import pytest


def test_basic():
    print("hello world")
    assert True


import pytest


@pytest.fixture
def temp_directory(tmp_path):
    # Create a temporary directory using tmp_path
    print(f"Temporary directory created: {tmp_path}")

    # Optionally, add files to the directory if needed
    test_file = tmp_path / "test.txt"
    test_file.write_text("Testing file access.")

    # Yield the temporary directory path to the test
    yield tmp_path

    # Cleanup happens automatically after the test


# Example test using the fixture
def test_file_access(temp_directory):
    # Access the temporary directory and file
    test_file = temp_directory / "test.txt"
    assert test_file.exists()
    assert test_file.read_text() == "Testing file access."