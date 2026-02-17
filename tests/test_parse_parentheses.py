from src.parse_parentheses import parse_parentheses


def test_single_character():
    """Test with a single character and no parentheses"""
    assert parse_parentheses("A") == ["A"]

def test_single_word_no_parentheses():
    """Test with a word and no parentheses"""
    assert parse_parentheses("Hello") == ["Hello"]

def test_parentheses_in_middle():
    """Test with parentheses in the middle of text"""
    assert parse_parentheses("A{{B}}C") == ["A", "B", "C"]

def test_start_with_parentheses():
    """Test when string starts with parentheses"""
    assert parse_parentheses("{{B}}C") == ["", "B", "C"]

def test_end_with_parentheses():
    """Test when string ends with parentheses"""
    assert parse_parentheses("{{B}}") == ["", "B", ""]

def test_multiple_parentheses_pairs():
    """Test with multiple parentheses pairs"""
    assert parse_parentheses("A{{B}}C{{D}}E") == ["A", "B", "C", "D", "E"]

def test_consecutive_parentheses():
    """Test with consecutive parentheses pairs"""
    assert parse_parentheses("A{{B}}{{D}}E") == ["A", "B", "", "D", "E"]

def test_empty_parentheses():
    """Test with empty parentheses"""
    assert parse_parentheses("A{{}}C{{}}") == ["A", "", "C", "", ""]

def test_only_parentheses():
    """Test with only parentheses and no text"""
    assert parse_parentheses("{{}}") == ["", "", ""]

def test_custom_delimiters():
    """Test with custom delimiters"""
    assert parse_parentheses("A<B>C", "<", ">") == ["A", "B", "C"]
    assert parse_parentheses("<B>C", "<", ">") == ["", "B", "C"]
    assert parse_parentheses("<B>", "<", ">") == ["", "B", ""]
    assert parse_parentheses("A<B><D>E", "<", ">") == ["A", "B", "", "D", "E"]

def test_longer_delimiters():
    """Test with longer delimiter strings"""
    assert parse_parentheses("A[[]B[]]C", "[[]", "[]]") == ["A", "B", "C"]
    assert parse_parentheses("[[]B[]]C", "[[]", "[]]") == ["", "B", "C"]
    assert parse_parentheses("[[]B[]]", "[[]", "[]]") == ["", "B", ""]

def test_empty_string():
    """Test with empty string"""
    assert parse_parentheses("") == [""]

def test_multibyte_characters():
    """Test with multibyte characters"""
    assert parse_parentheses("你好{{世界}}！") == ["你好", "世界", "！"]

def test_whitespace_handling():
    """Test with whitespace in the text"""
    assert parse_parentheses("  {{  }}  ") == ["  ", "  ", "  "]

def test_complex_scenario():
    """Test a more complex scenario"""
    result = parse_parentheses("pre{{first}}mid{{second}}post")
    assert result == ["pre", "first", "mid", "second", "post"]