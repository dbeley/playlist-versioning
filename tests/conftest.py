import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp, ignore_errors=True)


@pytest.fixture
def fixture_dir():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_favorite_tracks(fixture_dir):
    return fixture_dir / "00_favorite-tracks.txt"


@pytest.fixture
def sample_playlists(fixture_dir):
    return fixture_dir / "01_playlists.csv"


@pytest.fixture
def sample_artists(fixture_dir):
    return fixture_dir / "02_artists.csv"


@pytest.fixture
def sample_result_mplaylist(fixture_dir):
    return fixture_dir / "04_result-mplaylist.csv"


@pytest.fixture
def sample_result_missing(fixture_dir):
    return fixture_dir / "05_result-mplaylist-missing.csv"


@pytest.fixture
def sample_fix_missing(fixture_dir):
    return fixture_dir / "06_fix-missing-tracks.csv"


@pytest.fixture
def test_files_dir(temp_dir, fixture_dir):
    files_dir = temp_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    for fixture_file in fixture_dir.glob("*.csv"):
        shutil.copy(fixture_file, files_dir / fixture_file.name)
    for fixture_file in fixture_dir.glob("*.txt"):
        shutil.copy(fixture_file, files_dir / fixture_file.name)

    return temp_dir
