# test_process_chunks.py
import pytest
from src.process_chunks import process_chunks

def test_string_passthrough():
    assert process_chunks(['A']) == ['A']

def test_invalid_item_type():
    with pytest.raises(ValueError, match="Invalid item type"):
        process_chunks([5])

def test_invalid_sublist_length():
    with pytest.raises(ValueError, match="Invalid sub-list length"):
        process_chunks([['A']])

def test_invalid_list_item():
    with pytest.raises(ValueError, match="Invalid list item"):
        process_chunks([[5,6,7]])

def test_failed_json_parse():
    with pytest.raises(ValueError, match="Failed to parse JSON"):
        process_chunks([['A','B','C']])

def test_success_complex_json():
    input_list = [[
        '{"name": "John Doe", "email": "john@example.com", "age": 30, "active": true, "roles": ["admin", "user"], "address": {"street": "123 Main St", "city": "New York", "country": "USA"}, "projects": [{"id": 1, "name": "Website Redesign"}, {"id": 2, "name": "Mobile App"}]}',
        "B",
        '{"title": "John Doe"}'
    ]]
    expected = [{
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "active": True,
        "roles": ["admin", "user"],
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "country": "USA"
        },
        "projects": [
            {"id": 1, "name": "Website Redesign"},
            {"id": 2, "name": "Mobile App"}
        ]
    }, "B", {"title": "John Doe"}]
    assert process_chunks(input_list) == [expected]


def test_strings_passed_through():
    """Test that string items are passed through unchanged"""
    assert process_chunks(['A']) == ['A']
    assert process_chunks(['A', 'B', 'C']) == ['A', 'B', 'C']
    assert process_chunks([]) == []


def test_invalid_item_type():
    """Test that non-string non-list items raise ValueError"""
    with pytest.raises(ValueError, match="Invalid item type"):
        process_chunks([5])

    with pytest.raises(ValueError, match="Invalid item type"):
        process_chunks([None])

    with pytest.raises(ValueError, match="Invalid item type"):
        process_chunks([True])


def test_invalid_sub_list_length():
    """Test that sub-lists with length != 3 raise ValueError"""
    with pytest.raises(ValueError, match="Invalid sub-list length"):
        process_chunks([['A']])

    with pytest.raises(ValueError, match="Invalid sub-list length"):
        process_chunks([['A', 'B']])

    with pytest.raises(ValueError, match="Invalid sub-list length"):
        process_chunks([['A', 'B', 'C', 'D']])


def test_invalid_list_item_type():
    """Test that non-string items in sub-list raise ValueError"""
    with pytest.raises(ValueError, match="Invalid list item"):
        process_chunks([[5, 'B', 'C']])

    with pytest.raises(ValueError, match="Invalid list item"):
        process_chunks([['A', 5, 'C']])

    with pytest.raises(ValueError, match="Invalid list item"):
        process_chunks([['A', 'B', 5]])

    with pytest.raises(ValueError, match="Invalid list item"):
        process_chunks([[None, 'B', 'C']])


def test_invalid_json():
    """Test that invalid JSON strings raise ValueError"""
    with pytest.raises(ValueError, match="Failed to parse JSON"):
        process_chunks([['{invalid json}', 'B', '{"valid": "json"}']])

    with pytest.raises(ValueError, match="Failed to parse JSON"):
        process_chunks([['{"valid": "json"}', 'B', '{invalid json}']])

    with pytest.raises(ValueError, match="Failed to parse JSON"):
        process_chunks([['not json at all', 'B', 'also not json']])


def test_successful_json_parsing():
    """Test successful parsing of valid JSON strings"""
    input_data = [['{"name": "John", "age": 30}', 'middle', '{"city": "NYC"}']]
    expected = [[{"name": "John", "age": 30}, 'middle', {"city": "NYC"}]]

    result = process_chunks(input_data)
    assert result == expected
    assert isinstance(result[0][0], dict)
    assert isinstance(result[0][2], dict)


def test_complex_json_parsing():
    """Test parsing of complex nested JSON structures"""
    input_data = [[
        """
        {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30,
            "active": true,
            "roles": ["admin", "user"],
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "country": "USA"
            },
            "projects": [
                {"id": 1, "name": "Website Redesign"},
                {"id": 2, "name": "Mobile App"}
            ]
        }
        """,
        "B",
        """
        {
            "title": "John Doe"
        }
        """
    ]]

    result = process_chunks(input_data)

    # Verify first dictionary
    first_dict = result[0][0]
    assert first_dict["name"] == "John Doe"
    assert first_dict["email"] == "john@example.com"
    assert first_dict["age"] == 30
    assert first_dict["active"] is True
    assert first_dict["roles"] == ["admin", "user"]
    assert first_dict["address"]["street"] == "123 Main St"
    assert first_dict["address"]["city"] == "New York"
    assert first_dict["address"]["country"] == "USA"
    assert len(first_dict["projects"]) == 2
    assert first_dict["projects"][0]["name"] == "Website Redesign"
    assert first_dict["projects"][1]["name"] == "Mobile App"

    # Verify middle item
    assert result[0][1] == "B"

    # Verify third dictionary
    third_dict = result[0][2]
    assert third_dict["title"] == "John Doe"


def test_mixed_input():
    """Test with mixed input containing strings and sub-lists"""
    input_data = [
        'first string',
        ['{"x": 1}', 'middle1', '{"y": 2}'],
        'second string',
        ['{"a": true}', 'middle2', '{"b": false}'],
        'third string'
    ]

    expected = [
        'first string',
        [{"x": 1}, 'middle1', {"y": 2}],
        'second string',
        [{"a": True}, 'middle2', {"b": False}],
        'third string'
    ]

    result = process_chunks(input_data)
    assert result == expected

    # Verify types
    assert isinstance(result[0], str)
    assert isinstance(result[1][0], dict)
    assert isinstance(result[1][1], str)
    assert isinstance(result[1][2], dict)
    assert isinstance(result[2], str)
    assert isinstance(result[3][0], dict)
    assert isinstance(result[3][2], dict)
    assert isinstance(result[4], str)


def test_json_with_unicode():
    """Test parsing JSON with Unicode characters"""
    input_data = [['{"message": "Hello, 世界"}', 'sep', '{"greeting": "¡Hola!"}']]
    expected = [[{"message": "Hello, 世界"}, 'sep', {"greeting": "¡Hola!"}]]

    result = process_chunks(input_data)
    assert result == expected


def test_empty_json_objects():
    """Test parsing empty JSON objects"""
    input_data = [['{}', 'middle', '{}']]
    expected = [[{}, 'middle', {}]]

    result = process_chunks(input_data)
    assert result == expected




def test_string_pass_through():
    """Test that strings are passed through unchanged."""
    assert process_chunks(['A']) == ['A']
    assert process_chunks(['hello', 'world']) == ['hello', 'world']
    assert process_chunks([]) == []


def test_invalid_item_type_integer():
    """Test that integers raise ValueError with 'Invalid item type'."""
    with pytest.raises(ValueError, match="Invalid item type"):
        process_chunks([5])


def test_invalid_item_type_dict():
    """Test that dictionaries raise ValueError with 'Invalid item type'."""
    with pytest.raises(ValueError, match="Invalid item type"):
        process_chunks([{"key": "value"}])


def test_invalid_item_type_none():
    """Test that None raises ValueError with 'Invalid item type'."""
    with pytest.raises(ValueError, match="Invalid item type"):
        process_chunks([None])


def test_invalid_sub_list_length_one():
    """Test that sub-list with 1 item raises ValueError with 'Invalid sub-list length'."""
    with pytest.raises(ValueError, match="Invalid sub-list length"):
        process_chunks([['A']])


def test_invalid_sub_list_length_two():
    """Test that sub-list with 2 items raises ValueError with 'Invalid sub-list length'."""
    with pytest.raises(ValueError, match="Invalid sub-list length"):
        process_chunks([['A', 'B']])


def test_invalid_sub_list_length_four():
    """Test that sub-list with 4 items raises ValueError with 'Invalid sub-list length'."""
    with pytest.raises(ValueError, match="Invalid sub-list length"):
        process_chunks([['A', 'B', 'C', 'D']])


def test_invalid_list_item_integer():
    """Test that integer in sub-list raises ValueError with 'Invalid list item'."""
    with pytest.raises(ValueError, match="Invalid sub-list length"):
        process_chunks([[5]])


def test_invalid_list_item_dict():
    """Test that dict in sub-list raises ValueError with 'Invalid list item'."""
    with pytest.raises(ValueError, match="Invalid sub-list length"):
        process_chunks([[{"key": "value"}]])


def test_invalid_list_item_mixed():
    """Test that mixed types in sub-list raise ValueError with 'Invalid list item'."""
    with pytest.raises(ValueError, match="Invalid list item"):
        process_chunks([['A', 5, 'C']])


def test_failed_to_parse_json_first():
    """Test that invalid JSON in first position raises ValueError with 'Failed to parse JSON'."""
    with pytest.raises(ValueError, match="Failed to parse JSON"):
        process_chunks([['A', 'B', 'C']])


def test_failed_to_parse_json_third():
    """Test that invalid JSON in third position raises ValueError with 'Failed to parse JSON'."""
    with pytest.raises(ValueError, match="Failed to parse JSON"):
        process_chunks([['{"valid": true}', 'B', 'invalid json']])


def test_valid_json_parsing():
    """Test successful JSON parsing of first and third items."""
    json1 = '''{  "name": "John Doe",  "email": "john@example.com",  "age": 30,  "active": true,  "roles": ["admin", "user"],  "address": {    "street": "123 Main St",    "city": "New York",    "country": "USA"  },  "projects": [    {"id": 1, "name": "Website Redesign"},    {"id": 2, "name": "Mobile App"}  ] }'''
    json2 = '''{  "title": "John Doe" }'''

    result = process_chunks([[json1, "B", json2]])

    expected_first = {
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30,
        "active": True,
        "roles": ["admin", "user"],
        "address": {
            "street": "123 Main St",
            "city": "New York",
            "country": "USA"
        },
        "projects": [
            {"id": 1, "name": "Website Redesign"},
            {"id": 2, "name": "Mobile App"}
        ]
    }
    expected_third = {"title": "John Doe"}

    assert result[0][0] == expected_first
    assert result[0][1] == "B"
    assert result[0][2] == expected_third


def test_mixed_string_and_sublist():
    """Test that strings and sub-lists can be mixed."""
    result = process_chunks(['A', ['{"x": 1}', 'middle', '{"y": 2}'], 'B'])

    assert result[0] == 'A'
    assert result[1] == [{"x": 1}, 'middle', {"y": 2}]
    assert result[2] == 'B'


def test_empty_sublist():
    """Test that empty sub-list raises ValueError with 'Invalid sub-list length'."""
    with pytest.raises(ValueError, match="Invalid sub-list length"):
        process_chunks([[]])


def test_nested_list():
    """Test that nested list in sub-list raises ValueError with 'Invalid list item'."""
    with pytest.raises(ValueError, match="Invalid list item"):
        process_chunks([['A', ['nested'], 'C']])