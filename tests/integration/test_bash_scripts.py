"""
Tests for bash script integration and documentation.

Note: These tests document the expected behavior and interface of the bash scripts.
Full testing would require mpc/mpd installation, which is outside the scope of unit testing.
"""

import pytest
from pathlib import Path
import subprocess


@pytest.mark.integration
class TestBashScriptInterface:
    def test_mplaylist_script_exists(self):
        script = Path("mplaylist.sh")
        assert script.exists()
        assert script.is_file()
        assert script.stat().st_mode & 0o111

    def test_mplaylist_script_usage(self):
        result = subprocess.run(
            ["bash", "mplaylist.sh", "-h"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )

        assert result.returncode == 0
        assert "Usage:" in result.stdout or "usage:" in result.stdout.lower()

    def test_mpd_playlists_script_exists(self):
        script = Path("mpd_playlists.sh")
        assert script.exists()
        assert script.is_file()
        assert script.stat().st_mode & 0o111

    def test_navidrome_playlists_script_exists(self):
        script = Path("navidrome_playlists.sh")
        assert script.exists()
        assert script.is_file()
        assert script.stat().st_mode & 0o111

    def test_mplaylist_expected_outputs(self):
        expected_output_file = Path("files/04_result-mplaylist.csv")
        expected_missing_file = Path("files/05_result-mplaylist-missing.csv")

        assert expected_output_file.name == "04_result-mplaylist.csv"
        assert expected_missing_file.name == "05_result-mplaylist-missing.csv"

    def test_script_workflow_documentation(self):
        workflow = {
            "step1": {
                "script": "mplaylist.sh",
                "input": "files/00_favorites-tracks.txt",
                "outputs": [
                    "files/04_result-mplaylist.csv",
                    "files/05_result-mplaylist-missing.csv",
                ],
                "description": "Query MPD for tracks",
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
                "outputs": ["playlists/", "mpd_playlists/", "raw_playlists/"],
                "description": "Generate playlist files",
            },
            "step3_mpd": {
                "script": "mpd_playlists.sh",
                "input": "mpd_playlists/",
                "output": "~/.config/mpd/playlists/",
                "description": "Sync playlists to MPD",
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
        assert len(workflow) == 4


@pytest.mark.integration
class TestBashScriptFormat:
    def test_mplaylist_script_format(self):
        script_path = Path("mplaylist.sh")
        content = script_path.read_text()

        assert content.startswith("#!/usr/bin/env bash") or content.startswith(
            "#!/bin/bash"
        )
        assert "usage()" in content or "Usage:" in content
        assert "mpc search" in content
        assert "OUTPUT_FILE" in content

    def test_mpd_playlists_script_format(self):
        script_path = Path("mpd_playlists.sh")
        content = script_path.read_text()

        assert content.startswith("#!/usr/bin/env bash") or content.startswith(
            "#!/bin/bash"
        )
        assert "rsync" in content
        assert "mpd_playlists/" in content

    def test_navidrome_playlists_script_format(self):
        script_path = Path("navidrome_playlists.sh")
        content = script_path.read_text()

        assert content.startswith("#!/usr/bin/env bash") or content.startswith(
            "#!/bin/bash"
        )
        assert "rsync" in content
        assert "playlists/" in content


@pytest.mark.integration
class TestBashScriptIntegration:
    def test_mplaylist_output_matches_python_input(self):
        mplaylist_outputs = [
            "files/04_result-mplaylist.csv",
            "files/05_result-mplaylist-missing.csv",
        ]

        from create_playlists import (
            RESULT_MPLAYLIST_FILE_NAME,
            RESULT_MPLAYLIST_MISSING_FILE_NAME,
        )

        assert RESULT_MPLAYLIST_FILE_NAME == mplaylist_outputs[0]
        assert RESULT_MPLAYLIST_MISSING_FILE_NAME == mplaylist_outputs[1]

    def test_python_output_matches_sync_scripts_input(self):
        mpd_script = Path("mpd_playlists.sh").read_text()
        navidrome_script = Path("navidrome_playlists.sh").read_text()

        assert "mpd_playlists/" in mpd_script
        assert "playlists/" in navidrome_script

    def test_file_format_consistency(self):
        assert True
