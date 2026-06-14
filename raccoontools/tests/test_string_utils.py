import pytest

from raccoontools.shared.string_utils import linefy


class TestLinefy:
    def test_removes_linebreaks(self):
        assert linefy("line one\nline two\nline three") == "line one line two line three"

    def test_removes_carriage_returns(self):
        assert linefy("line one\r\nline two") == "line one line two"

    def test_collapses_multiple_spaces(self):
        assert linefy("too     many      spaces") == "too many spaces"

    def test_collapses_tabs(self):
        assert linefy("tab\tseparated\tvalues") == "tab separated values"

    def test_collapses_mixed_whitespace(self):
        assert linefy("mixed \t \n  whitespace") == "mixed whitespace"

    def test_trims_leading_whitespace(self):
        assert linefy("   leading") == "leading"

    def test_trims_trailing_whitespace(self):
        assert linefy("trailing   ") == "trailing"

    def test_trims_leading_and_trailing_whitespace(self):
        assert linefy("  both sides  ") == "both sides"

    def test_combined_scenario(self):
        text = "  Hello\n\tworld  \n  again  "
        assert linefy(text) == "Hello world again"

    def test_combined_scenario_using_literal(self):
        text = """Hello world\t\tafter tabs!
        Ping?
        
        Pong!\t
        """
        assert linefy(text) == "Hello world after tabs! Ping? Pong!"

    def test_already_clean_string_is_unchanged(self):
        assert linefy("already clean") == "already clean"

    def test_single_word(self):
        assert linefy("word") == "word"

    def test_empty_string_returns_empty(self):
        assert linefy("") == ""

    def test_whitespace_only_returns_empty(self):
        assert linefy("   \n\t\r  ") == ""

    def test_preserves_internal_word_characters(self):
        assert linefy("don't\nbreak-this_word") == "don't break-this_word"

    def test_unicode_whitespace_is_collapsed(self):
        # Non-breaking space (\xa0) and other unicode spaces are whitespace to str.split().
        assert linefy("a\xa0\xa0b") == "a b"

    @pytest.mark.parametrize(
        "value",
        [None, 123, 4.5, ["a", "b"], {"a": 1}, b"bytes"],
    )
    def test_non_string_input_raises_type_error(self, value):
        with pytest.raises(TypeError):
            linefy(value)
