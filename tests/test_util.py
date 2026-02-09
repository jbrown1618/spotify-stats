"""Tests for utils/util.py functions"""
import pytest
from utils.util import get_id, spotify_url, file_name_friendly, first
import pandas as pd


class TestGetId:
    """Test get_id function"""
    
    def test_track_uri(self):
        uri = "spotify:track:abc123def456"
        assert get_id(uri) == "abc123def456"
    
    def test_artist_uri(self):
        uri = "spotify:artist:xyz789"
        assert get_id(uri) == "xyz789"
    
    def test_album_uri(self):
        uri = "spotify:album:album123"
        assert get_id(uri) == "album123"


class TestSpotifyUrl:
    """Test spotify_url function"""
    
    def test_track_url(self):
        uri = "spotify:track:abc123"
        expected = "https://open.spotify.com/track/abc123"
        assert spotify_url(uri) == expected
    
    def test_artist_url(self):
        uri = "spotify:artist:xyz789"
        expected = "https://open.spotify.com/artist/xyz789"
        assert spotify_url(uri) == expected
    
    def test_album_url(self):
        uri = "spotify:album:album123"
        expected = "https://open.spotify.com/album/album123"
        assert spotify_url(uri) == expected


class TestFileNameFriendly:
    """Test file_name_friendly function"""
    
    def test_basic_text(self):
        assert file_name_friendly("Hello World") == "hello_world"
    
    def test_special_characters(self):
        assert file_name_friendly("Test & File #1") == "test___file__1"
    
    def test_symbols(self):
        assert file_name_friendly("100% Sure? Yes!") == "100__sure__yes!"
    
    def test_quotes_and_slashes(self):
        assert file_name_friendly("Track's \"Best\" Song/Mix") == "track_s__best__song_mix"


class TestFirst:
    """Test first function"""
    
    def test_with_values(self):
        series = pd.Series([1, 2, 3, 4, 5])
        assert first(series) == 1
    
    def test_empty_series(self):
        series = pd.Series([])
        assert first(series) is None
    
    def test_single_value(self):
        series = pd.Series(['only'])
        assert first(series) == 'only'
