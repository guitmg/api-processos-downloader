"""
Tests for utils module.
"""

import pytest
from src.pje_automation.utils import (clean_filename, format_file_size,
                                      parse_process_number)


class TestParseProcessNumber:
    """Test process number parsing functionality."""

    def test_valid_process_number(self):
        """Test parsing a valid process number."""
        result = parse_process_number("5100342-29.2017.8.13.0024")

        expected = {
            "sequential": "5100342",
            "digit": "29",
            "year": "2017",
            "court": "0024",
        }

        assert result == expected

    def test_invalid_format(self):
        """Test parsing an invalid process number format."""
        with pytest.raises(ValueError):
            parse_process_number("invalid-format")

    def test_missing_parts(self):
        """Test parsing a process number with missing parts."""
        with pytest.raises(ValueError):
            parse_process_number("5100342-29.2017")


class TestFormatFileSize:
    """Test file size formatting functionality."""

    def test_bytes(self):
        """Test formatting bytes."""
        assert format_file_size(500) == "500.0 B"

    def test_kilobytes(self):
        """Test formatting kilobytes."""
        assert format_file_size(1536) == "1.5 KB"

    def test_megabytes(self):
        """Test formatting megabytes."""
        assert format_file_size(1572864) == "1.5 MB"

    def test_zero_size(self):
        """Test formatting zero size."""
        assert format_file_size(0) == "0 B"


class TestCleanFilename:
    """Test filename cleaning functionality."""

    def test_clean_valid_filename(self):
        """Test cleaning a valid filename."""
        result = clean_filename("document.pdf")
        assert result == "document.pdf"

    def test_clean_invalid_characters(self):
        """Test cleaning a filename with invalid characters."""
        result = clean_filename("doc<ument>:file?.pdf")
        assert result == "doc_ument__file_.pdf"

    def test_clean_empty_filename(self):
        """Test cleaning an empty filename."""
        result = clean_filename("")
        assert result == ""
