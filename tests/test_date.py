"""Tests for utils/date.py functions"""
import pytest
from utils.date import release_year


class TestReleaseYear:
    """Test release_year function"""
    
    def test_valid_year(self):
        assert release_year("2023-05-15") == "2023"
    
    def test_different_year(self):
        assert release_year("1999-12-31") == "1999"
    
    def test_just_year(self):
        assert release_year("2020") == "2020"
    
    def test_invalid_date(self):
        assert release_year("abcd-ef-gh") is None
    
    def test_empty_string(self):
        result = release_year("")
        # First 4 characters of empty string would be empty
        assert result is None or result == ""
