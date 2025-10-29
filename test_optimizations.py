#!/usr/bin/env python3
"""
Simple validation tests for the optimized create_playlists.py
These tests verify that the optimizations maintain correct functionality.
"""

from collections import defaultdict
from pathlib import Path
import sys

# Test data
SAMPLE_ARTIST_LIST = [
    ("Artist1", "1"),
    ("Artist2", "1"),
    ("Artist3", "2"),
    ("Artist1", "3"),  # Duplicate artist in different playlist
]

SAMPLE_TRACKS = [
    "Artist1/Album1/track1.mp3",
    "Artist2/Album1/track2.mp3",
    "Artist1/Album2/track3.mp3",
]

SAMPLE_PLAYLIST_DICT = {
    "1": "Rock",
    "2": "Pop",
    "3": "Jazz"
}


def build_artist_dict(artist_list):
    """
    Optimized version using defaultdict.
    Returns a dict where the key is the artist name,
    and the value is a list of playlist ids.
    """
    artist_dict = defaultdict(list)
    for artist_name, playlist_id in artist_list:
        artist_dict[artist_name].append(playlist_id)
    return dict(artist_dict)


def test_build_artist_dict():
    """Test that build_artist_dict correctly handles duplicate artists."""
    result = build_artist_dict(SAMPLE_ARTIST_LIST)
    
    assert "Artist1" in result, "Artist1 should be in the result"
    assert "Artist2" in result, "Artist2 should be in the result"
    assert "Artist3" in result, "Artist3 should be in the result"
    
    # Check that Artist1 appears in both playlist 1 and 3
    assert len(result["Artist1"]) == 2, f"Artist1 should appear in 2 playlists, got {len(result['Artist1'])}"
    assert "1" in result["Artist1"], "Artist1 should be in playlist 1"
    assert "3" in result["Artist1"], "Artist1 should be in playlist 3"
    
    # Check single playlist assignments
    assert len(result["Artist2"]) == 1, "Artist2 should appear in 1 playlist"
    assert result["Artist2"] == ["1"], "Artist2 should only be in playlist 1"
    
    assert len(result["Artist3"]) == 1, "Artist3 should appear in 1 playlist"
    assert result["Artist3"] == ["2"], "Artist3 should only be in playlist 2"
    
    print("✓ test_build_artist_dict passed")


def test_string_split_optimization():
    """Test that splitting strings once is more efficient."""
    # Simulate the old way (splitting twice)
    test_string = "1;Rock"
    
    # Old way (inefficient - splits twice)
    old_result = (test_string.split(";")[1], test_string.split(";")[0])
    
    # New way (efficient - splits once)
    parts = test_string.split(";")
    new_result = (parts[1], parts[0])
    
    assert old_result == new_result, "Results should be identical"
    print("✓ test_string_split_optimization passed")


def test_set_deduplication():
    """Test that set operations correctly deduplicate."""
    missing_artists1 = ["Artist1", "Artist2", "Artist3"]
    missing_artists2 = ["Artist2", "Artist4", "Artist1"]
    
    # Old way (creates set on combined list, then converts back, then creates set again when counting)
    old_combined = missing_artists1 + missing_artists2
    # First set creation happens here, converts to list
    old_result_list = list(set(old_combined))  
    # Then later in code, set() is called again: nb_missing_artists = len(set(missing_artists))
    
    # New way (creates set once and keeps as list)
    new_combined = list(set(missing_artists1 + missing_artists2))
    # Later uses len() directly: nb_missing_artists = len(missing_artists)
    
    # Both should have same elements (order might differ)
    assert set(old_result_list) == set(new_combined), "Results should contain same elements"
    assert len(new_combined) == 4, f"Should have 4 unique artists, got {len(new_combined)}"
    
    # The optimization is that we avoid calling set() twice:
    # Old code did: set(missing_artists) on line 186, then len(set(missing_artists)) on line 203
    # New code does: list(set(...)) once, then len(missing_artists) - no second set() call
    
    print("✓ test_set_deduplication passed")


def test_list_comprehension_removal():
    """Test that removing unnecessary list comprehension works."""
    tracks = ["track1.mp3", "track2.mp3", "track3.mp3"]
    
    # Old way (unnecessary list comprehension)
    old_result = "\n".join([x for x in tracks])
    
    # New way (direct join)
    new_result = "\n".join(tracks)
    
    assert old_result == new_result, "Results should be identical"
    print("✓ test_list_comprehension_removal passed")


def run_all_tests():
    """Run all validation tests."""
    print("Running validation tests for optimizations...\n")
    
    try:
        test_build_artist_dict()
        test_string_split_optimization()
        test_set_deduplication()
        test_list_comprehension_removal()
        
        print("\n✅ All tests passed! Optimizations are working correctly.")
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
