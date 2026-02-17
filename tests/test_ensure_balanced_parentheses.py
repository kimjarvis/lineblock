import pytest
from src.ensure_balanced_parentheses import ensure_balanced_parentheses

class TestEnsureBalancedParentheses:

    def test_empty_string(self):
        """Test that empty string passes validation"""
        ensure_balanced_parentheses("")

    def test_valid_simple_case(self):
        """Test valid case with spaces"""
        ensure_balanced_parentheses("{{ }}")

    def test_valid_no_spaces(self):
        """Test valid case without spaces"""
        ensure_balanced_parentheses("{{}}")

    def test_valid_with_text(self):
        """Test valid case with text between parentheses"""
        ensure_balanced_parentheses("{{ hello world }}")

    def test_valid_multiple_pairs(self):
        """Test valid case with multiple separate parentheses pairs"""
        ensure_balanced_parentheses("{{first}} {{second}}")

    def test_valid_with_special_characters(self):
        """Test valid case with special characters"""
        ensure_balanced_parentheses("{{ !@#$%^&*() }}")

    def test_nested_parentheses_raises_error(self):
        """Test that nested parentheses raise ValueError"""
        with pytest.raises(ValueError, match="Parentheses cannot be nested"):
            ensure_balanced_parentheses("{{ {{ }} }}")

    def test_nested_with_unclosed_raises_nesting_error(self):
        """Test that nested parentheses take precedence over unbalanced check"""
        with pytest.raises(ValueError, match="Parentheses cannot be nested"):
            ensure_balanced_parentheses("{{ {{ }}")  # This is nested first, then unbalanced

    def test_unmatched_opening_raises_error(self):
        """Test that unmatched opening parentheses raise ValueError"""
        with pytest.raises(ValueError, match="Parentheses are not matched"):
            ensure_balanced_parentheses("{{ hello")

    def test_unmatched_closing_raises_error(self):
        """Test that unmatched closing parentheses raise ValueError"""
        with pytest.raises(ValueError, match="Parentheses are not matched"):
            ensure_balanced_parentheses("hello }}")

    def test_only_opening_raises_error(self):
        """Test that only opening parentheses raise ValueError"""
        with pytest.raises(ValueError, match="Parentheses are not matched"):
            ensure_balanced_parentheses("{{")

    def test_only_closing_raises_error(self):
        """Test that only closing parentheses raise ValueError"""
        with pytest.raises(ValueError, match="Parentheses are not matched"):
            ensure_balanced_parentheses("}}")

    def test_custom_parentheses_different_check(self):
        """Test that using same custom parentheses raises error"""
        with pytest.raises(ValueError, match="Opening and closing parentheses must be different"):
            ensure_balanced_parentheses("test", "##", "##")

    def test_custom_parentheses_character_overlap(self):
        """Test that overlapping parentheses characters raise error"""
        with pytest.raises(ValueError,
                           match="The last character of open_parentheses cannot be the same as the first character of close_parentheses"):
            ensure_balanced_parentheses("test", "[{", "{]")

    def test_custom_parentheses_valid(self):
        """Test valid case with custom parentheses"""
        ensure_balanced_parentheses("<< hello >>", "<<", ">>")

    def test_custom_parentheses_with_different_lengths(self):
        """Test valid case with custom parentheses of different lengths"""
        ensure_balanced_parentheses("((hello))", "(((", ")))")

    def test_complex_valid_case(self):
        """Test complex valid case with multiple tokens"""
        ensure_balanced_parentheses("{{ token1 }} text {{ token2 }} more text {{ token3 }}")

    def test_incomplete_opening_doesnt_match(self):
        """Test that incomplete parentheses don't trigger matches"""
        ensure_balanced_parentheses("{ hello }")  # Single braces shouldn't match