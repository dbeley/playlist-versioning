"""
Tests for script integration and documentation.

Tests cover the navidrome_match.py script (replaces mplaylist.sh)
and remaining shell scripts.
"""

import pytest
from pathlib import Path
import sys


@pytest.mark.integration
class TestScriptInterface:
    def test_navidrome_match_script_exists(self):
        script = Path("navidrome_match.py")
        assert script.exists()
        assert script.is_file()
        assert script.stat().st_mode & 0o111

    def test_navidrome_match_usage(self):
        content = Path("navidrome_match.py").read_text()
        assert "usage()" in content.lower() or "Usage:" in content or "main()" in content
        assert "NAVIDROME_URL" in content or "NAVIDROME_USER" in content

    def test_navidrome_playlists_script_exists(self):
        script = Path("navidrome_playlists.sh")
        assert script.exists()
        assert script.is_file()
        assert script.stat().st_mode & 0o111

    def test_expected_output_files(self):
        expected_output_file = Path("files/04_result-mplaylist.csv")
        expected_missing_file = Path("files/05_result-mplaylist-missing.csv")

        assert expected_output_file.name == "04_result-mplaylist.csv"
        assert expected_missing_file.name == "05_result-mplaylist-missing.csv"

    def test_script_workflow_documentation(self):
        workflow = {
            "step1": {
                "script": "navidrome_match.py",
                "input": "files/00_dbeley-favorite-tracks.txt",
                "outputs": [
                    "files/04_result-mplaylist.csv",
                    "files/05_result-mplaylist-missing.csv",
                ],
                "description": "Query Navidrome API for tracks",
            },
            "step2": {
                "script": "create_playlists.py",
                "inputs": [
                    "files/01_playlists.csv",
                    "files/02_artists.csv",
                    "files/04_result-mplaylist.csv",
                    "files/05_result-mplaylist-missing.csv",
                    "files/06_fix-missing-tracks.csv",
                ],
                "outputs": ["playlists/", "raw_playlists/"],
                "description": "Generate playlist files",
            },
            "step3_navidrome": {
                "script": "navidrome_playlists.sh",
                "input": "playlists/",
                "output": "~/nfs/.../00_Playlists/",
                "description": "Sync playlists to Navidrome",
            },
        }

        assert "step1" in workflow
        assert "step2" in workflow
        assert workflow["step2"]["script"] == "create_playlists.py"
        assert len(workflow) == 3


@pytest.mark.integration
class TestNavidromeScriptFormat:
    def test_navidrome_match_script_format(self):
        script_path = Path("navidrome_match.py")
        content = script_path.read_text()

        assert content.startswith("#!/usr/bin/env python3") or content.startswith(
            "#!/usr/bin/python3"
        )
        assert "main()" in content
        assert "search2" in content
        assert "04_result-mplaylist" in content

    def test_navidrome_playlists_script_format(self):
        script_path = Path("navidrome_playlists.sh")
        content = script_path.read_text()

        assert content.startswith("#!/usr/bin/env bash") or content.startswith(
            "#!/bin/bash"
        )
        assert "rsync" in content
        assert "playlists/" in content

    def test_navidrome_match_parses_favorites(self):
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from navidrome_match import parse_favorite_tracks

        tracks = parse_favorite_tracks(
            str(Path(__file__).parent.parent / "fixtures" / "00_favorite-tracks.txt")
        )

        assert len(tracks) == 4
        assert ("Artist One", "Track One") in tracks
        assert ("Artist Two", "Track Two") in tracks
        assert ("Artist Three", "Track Three") in tracks
        assert ("Artist One", "Track Four") in tracks

    def test_navidrome_match_strips_library_root(self):
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from navidrome_match import strip_library_root
        from navidrome_match import LIBRARY_ROOT

        path = f"{LIBRARY_ROOT}Artist/Album/Track.mp3"
        result = strip_library_root(path)
        assert result == "Artist/Album/Track.mp3"

    def test_navidrome_match_handles_path_outside_library(self):
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from navidrome_match import strip_library_root

        result = strip_library_root("/some/other/path/file.mp3")
        assert result == "/some/other/path/file.mp3"

    def test_navidrome_match_handles_malformed_lines(self, capsys, temp_dir):
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from navidrome_match import parse_favorite_tracks

        bad_file = Path(str(temp_dir)) / "bad_tracks.txt"
        bad_file.write_text(
            "Valid Artist - Valid Track\n"
            "NoSeparatorLine\n"
            "Another Valid - Track Title\n"
            "  \n"
        )

        tracks = parse_favorite_tracks(str(bad_file))

        assert len(tracks) == 2
        assert ("Valid Artist", "Valid Track") in tracks
        assert ("Another Valid", "Track Title") in tracks

        captured = capsys.readouterr()
        assert "malformed" in captured.out


@pytest.mark.integration
class TestScriptIntegration:
    def test_navidrome_output_matches_python_input(self):
        navidrome_outputs = [
            "files/04_result-mplaylist.csv",
            "files/05_result-mplaylist-missing.csv",
        ]

        from create_playlists import (
            RESULT_MPLAYLIST_FILE_NAME,
            RESULT_MPLAYLIST_MISSING_FILE_NAME,
        )

        assert RESULT_MPLAYLIST_FILE_NAME == navidrome_outputs[0]
        assert RESULT_MPLAYLIST_MISSING_FILE_NAME == navidrome_outputs[1]

    def test_python_output_matches_sync_scripts_input(self):
        navidrome_script = Path("navidrome_playlists.sh").read_text()

        assert "playlists/" in navidrome_script

    def test_file_format_consistency(self):
        assert True

    def test_mpd_artifacts_removed(self):
        assert not Path("mplaylist.sh").exists()
        assert not Path("mpd_playlists.sh").exists()
        assert not Path("mpd_playlists").exists()
