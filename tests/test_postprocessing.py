from ocr.merge_broken_words import merge_broken_words
from ocr.unique_words import extract_unique_words


class TestMergeBrokenWords:
    def test_hyphenation_join(self):
        result = merge_broken_words("word-\nbreak")
        assert "wordbreak" in result

    def test_multiple_newlines_collapsed(self):
        result = merge_broken_words("hello\n\n\nworld")
        assert "hello world" in result

    def test_no_hyphenation(self):
        result = merge_broken_words("hello world\nfoo bar")
        assert "hello world foo bar" == result


class TestUniqueWords:
    def test_extract_unique_words(self):
        result = extract_unique_words("Hello hello World")
        assert result == {"hello", "world"}

    def test_empty_string(self):
        result = extract_unique_words("")
        assert result == set()

    def test_numbers_ignored(self):
        result = extract_unique_words("hello 123 world 456")
        assert result == {"hello", "world"}
