"""
Smoke test to verify test infrastructure is working.
"""

import pytest


def test_pytest_works():
    assert True


def test_fixtures_exist(fixture_dir):
    assert fixture_dir.exists()
    assert fixture_dir.is_dir()
    assert len(list(fixture_dir.glob("*"))) > 0


def test_temp_dir_fixture(temp_dir):
    assert temp_dir.exists()
    assert temp_dir.is_dir()


def test_sample_files_exist(sample_favorite_tracks, sample_playlists, sample_artists):
    assert sample_favorite_tracks.exists()
    assert sample_playlists.exists()
    assert sample_artists.exists()


@pytest.mark.unit
def test_marker_unit():
    assert True


@pytest.mark.integration
def test_marker_integration():
    assert True


@pytest.mark.e2e
def test_marker_e2e():
    assert True
