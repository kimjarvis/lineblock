import pytest
from src.isolate_blocks import isolate_blocks

def test_single_item():
    """Test with a single item (n=0)"""
    assert isolate_blocks(["A"]) == ["A"]

def test_five_items():
    """Test with 5 items (n=1)"""
    result = isolate_blocks(["A", "B", "C", "D", "E"])
    assert result == ["A", ["B", "C", "D"], "E"]

def test_nine_items():
    """Test with 9 items (n=2)"""
    result = isolate_blocks(["A", "B", "C", "D", "E", "F", "G", "H", "I"])
    assert result == ["A", ["B", "C", "D"], "E", ["F", "G", "H"], "I"]

def test_thirteen_items():
    """Test with 13 items (n=3)"""
    items = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"]
    expected = ["A", ["B", "C", "D"], "E", ["F", "G", "H"], "I", ["J", "K", "L"], "M"]
    assert isolate_blocks(items) == expected

def test_invalid_length_raises_error():
    """Test that invalid list length raises ValueError"""
    with pytest.raises(ValueError, match="Invalid blocks"):
        isolate_blocks(["A", "B"])  # 2 items (should be 1, 5, 9, etc.)

def test_non_string_items_raises_error():
    """Test that non-string items raise ValueError"""
    with pytest.raises(ValueError, match="Invalid items"):
        isolate_blocks([5, "B", "C", "D", "E"])  # First item is int, not string

def test_mixed_types_raises_error():
    """Test that mixed type list raises ValueError"""
    with pytest.raises(ValueError, match="Invalid items"):
        isolate_blocks(["A", 2, 3, 4, "E"])  # Middle items are ints

def test_empty_list_raises_error():
    """Test that empty list raises ValueError (0 items, not 1 mod 4)"""
    with pytest.raises(ValueError, match="Invalid blocks"):
        isolate_blocks([])

def test_three_items_raises_error():
    """Test that 3 items raises ValueError"""
    with pytest.raises(ValueError, match="Invalid blocks"):
        isolate_blocks(["A", "B", "C"])

def test_complex_strings():
    """Test with various string values"""
    items = ["hello", "world", "foo", "bar", "baz"]
    result = isolate_blocks(items)
    assert result == ["hello", ["world", "foo", "bar"], "baz"]