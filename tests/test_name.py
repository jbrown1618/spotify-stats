"""Tests for utils/name.py functions"""
import pytest
import pandas as pd
from utils.name import short_name, is_disposable


class TestShortName:
    """Test short_name function"""
    
    def test_basic_name(self):
        assert short_name("Album Name") == "Album Name"
    
    def test_with_remaster_suffix(self):
        assert short_name("Great Album - Remastered") == "Great Album"
    
    def test_with_deluxe_suffix(self):
        assert short_name("Best Hits - Deluxe Edition") == "Best Hits"
    
    def test_with_remaster_parenthetical(self):
        assert short_name("Album Title (Remastered)") == "Album Title "
    
    def test_with_deluxe_parenthetical(self):
        assert short_name("Songs (Deluxe)") == "Songs "
    
    def test_quoted_name_with_disposable_prefix(self):
        assert short_name("Remastered \"Original Title\"") == "Original Title"
    
    def test_na_value(self):
        result = short_name(pd.NA)
        assert pd.isna(result)
    
    def test_no_disposable_content(self):
        assert short_name("Album (Special Edition)") == "Album (Special Edition)"


class TestIsDisposable:
    """Test is_disposable function"""
    
    def test_remaster(self):
        assert is_disposable("Remastered") is True
    
    def test_deluxe(self):
        assert is_disposable("Deluxe Edition") is True
    
    def test_soundtrack(self):
        assert is_disposable("Original Soundtrack") is True
    
    def test_bonus(self):
        assert is_disposable("Bonus Track") is True
    
    def test_album_index(self):
        assert is_disposable("1st album") is True
        assert is_disposable("2nd album") is True
        assert is_disposable("3rd album") is True
        assert is_disposable("4th album") is True
    
    def test_mini_album(self):
        assert is_disposable("1st mini album") is True
    
    def test_non_disposable(self):
        assert is_disposable("Special Edition") is False
    
    def test_case_insensitive(self):
        assert is_disposable("REMASTER") is True
        assert is_disposable("DeLuXe") is True
