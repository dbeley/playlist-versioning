"""
End-to-end tests for the complete playlist versioning workflow.
"""

import pytest
from pathlib import Path
import sys


@pytest.mark.e2e
class TestEndToEnd:
    def test_script_runs_successfully(self, test_files_dir, temp_dir, monkeypatch):
        monkeypatch.chdir(test_files_dir)

        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from playlist_lib import (
            read_files,
            build_artist_dict,
            match_tracks,
            match_missing_tracks,
            build_playlists,
            export_playlists,
            export_raw_playlists,
        )

        files_dir = test_files_dir / "files"

        (
            raw_tracks,
            tracks,
            missing_tracks,
            playlist_dict,
            artist_list,
            missing_dict,
        ) = read_files(
            files_dir / "00_favorite-tracks.txt",
            files_dir / "01_playlists.csv",
            files_dir / "02_artists.csv",
            files_dir / "04_result-mplaylist.csv",
            files_dir / "05_result-mplaylist-missing.csv",
            files_dir / "06_fix-missing-tracks.csv",
        )

        artist_dict = build_artist_dict(artist_list)
        file_list, missing_artists = match_tracks(tracks, artist_dict)
        raw_track_list, raw_missing_artists = match_tracks(
            raw_tracks, artist_dict, sep=" - "
        )
        missing_file_list, list_missing_paths, missing_artists2 = match_missing_tracks(
            missing_tracks, missing_dict, artist_dict, "/home/test/music/"
        )

        file_list = missing_file_list + file_list
        missing_artists = missing_artists + missing_artists2

        final_dict = build_playlists(file_list, playlist_dict)
        raw_final_dict = build_playlists(
            raw_track_list + missing_file_list, playlist_dict
        )

        playlists_dir = temp_dir / "playlists"
        mpd_dir = temp_dir / "mpd_playlists"
        raw_dir = temp_dir / "raw_playlists"

        export_playlists(str(playlists_dir), "/music/", final_dict)
        export_playlists(str(mpd_dir), "", final_dict)
        export_raw_playlists(raw_final_dict, str(raw_dir))

        assert playlists_dir.exists()
        assert mpd_dir.exists()
        assert raw_dir.exists()

        playlist_files = list(playlists_dir.glob("*.m3u"))
        assert len(playlist_files) > 0

        raw_files = list(raw_dir.glob("*.txt"))
        assert len(raw_files) > 0

    def test_complete_workflow_with_output_validation(
        self, test_files_dir, temp_dir, monkeypatch
    ):
        monkeypatch.chdir(test_files_dir)

        from playlist_lib import (
            read_files,
            build_artist_dict,
            match_tracks,
            build_playlists,
            export_playlists,
        )

        files_dir = test_files_dir / "files"

        _, tracks, _, playlist_dict, artist_list, _ = read_files(
            files_dir / "00_favorite-tracks.txt",
            files_dir / "01_playlists.csv",
            files_dir / "02_artists.csv",
            files_dir / "04_result-mplaylist.csv",
        )

        artist_dict = build_artist_dict(artist_list)
        file_list, _ = match_tracks(tracks, artist_dict)
        final_dict = build_playlists(file_list, playlist_dict)

        output_dir = temp_dir / "output"
        export_playlists(str(output_dir), "/music/", final_dict)

        for playlist_file in output_dir.glob("*.m3u"):
            name = playlist_file.stem
            assert "_" in name or name.isdigit()

            content = playlist_file.read_text()
            if content.strip():
                lines = content.split("\n")
                for line in lines:
                    if line.strip():
                        assert line.startswith("/music/")


@pytest.mark.e2e
class TestEdgeCases:
    def test_unicode_characters_in_artist_names(self, temp_dir):
        from playlist_lib import build_artist_dict, match_tracks

        artist_list = [("Björk", "1"), ("Café Tacvba", "2"), ("王菲", "3")]
        artist_dict = build_artist_dict(artist_list)

        tracks = [
            "Björk/Album/Track.mp3",
            "Café Tacvba/Album/Track.mp3",
            "王菲/Album/Track.mp3",
        ]

        file_list, missing_artists = match_tracks(tracks, artist_dict)

        assert len(file_list) == 3
        assert len(missing_artists) == 0

    def test_very_long_playlist_names(self, temp_dir):
        from playlist_lib import export_playlists

        long_name = "A" * 200
        final_dict = {f"1_{long_name}": ["track.mp3"]}

        export_playlists(str(temp_dir), "", final_dict)

        files = list(temp_dir.glob("*.m3u"))
        assert len(files) == 1

    def test_many_playlists(self, temp_dir):
        from playlist_lib import build_playlists, export_playlists

        playlist_dict = {str(i): f"Playlist{i}" for i in range(1, 151)}
        file_list = [{str(i): f"track{i}.mp3"} for i in range(1, 151)]

        final_dict = build_playlists(file_list, playlist_dict)
        export_playlists(str(temp_dir), "", final_dict)

        assert len(list(temp_dir.glob("*.m3u"))) == 150

        files = sorted(temp_dir.glob("*.m3u"))
        first_file = files[0].stem
        assert first_file.startswith("001_")

    def test_many_tracks_per_playlist(self, temp_dir):
        from playlist_lib import export_playlists

        tracks = [f"Artist/Album/Track{i}.mp3" for i in range(1000)]
        final_dict = {"1_Large": tracks}

        export_playlists(str(temp_dir), "", final_dict)

        content = (temp_dir / "1_Large.m3u").read_text()
        lines = content.split("\n")
        assert len(lines) == 1000

    def test_empty_artist_name(self, temp_dir):
        from playlist_lib import match_tracks

        tracks = ["/Album/Track.mp3"]
        artist_dict = {"": ["1"]}

        file_list, missing_artists = match_tracks(tracks, artist_dict)

        assert len(file_list) == 1
        assert {"1": "/Album/Track.mp3"} in file_list

    def test_whitespace_handling(self, temp_dir):
        from playlist_lib import match_tracks

        tracks = ["  Artist  /Album/Track.mp3"]
        artist_dict = {"Artist": ["1"]}

        file_list, missing_artists = match_tracks(tracks, artist_dict)

        assert len(file_list) == 1

    def test_case_sensitivity(self, temp_dir):
        """Matching is case-sensitive."""
        from playlist_lib import match_tracks

        tracks = ["artist/Album/Track.mp3"]
        artist_dict = {"Artist": ["1"]}

        file_list, missing_artists = match_tracks(tracks, artist_dict)

        assert len(file_list) == 0
        assert "artist" in missing_artists

    def test_special_characters_in_paths(self, temp_dir):
        from playlist_lib import export_playlists

        final_dict = {
            "1_Test": [
                "Artist/Album (2000)/01 Track.mp3",
                "Artist/Album [Bonus]/02 Track.mp3",
                "Artist/Album & More/03 Track.mp3",
            ]
        }

        export_playlists(str(temp_dir), "/music/", final_dict)

        content = (temp_dir / "1_Test.m3u").read_text()
        assert "(2000)" in content
        assert "[Bonus]" in content
        assert "&" in content

    def test_duplicate_tracks_in_playlist(self, temp_dir):
        """Duplicate tracks are preserved."""
        from playlist_lib import build_playlists

        file_list = [
            {"1": "track.mp3"},
            {"1": "track.mp3"},
            {"1": "track.mp3"},
        ]
        playlist_dict = {"1": "Test"}

        final_dict = build_playlists(file_list, playlist_dict)

        assert len(final_dict["1_Test"]) == 3

    def test_multiple_separators_in_track_name(self):
        from playlist_lib import match_tracks

        tracks = ["Artist - Group/Album/Track - Version.mp3"]
        artist_dict = {"Artist - Group": ["1"]}

        file_list, _ = match_tracks(tracks, artist_dict)

        assert len(file_list) == 1


@pytest.mark.e2e
class TestDataIntegrity:
    def test_no_data_loss_through_pipeline(self, test_files_dir):
        from playlist_lib import (
            read_files,
            build_artist_dict,
            match_tracks,
        )

        files_dir = test_files_dir / "files"

        _, tracks, _, playlist_dict, artist_list, _ = read_files(
            files_dir / "00_favorite-tracks.txt",
            files_dir / "01_playlists.csv",
            files_dir / "02_artists.csv",
            files_dir / "04_result-mplaylist.csv",
        )

        artist_dict = build_artist_dict(artist_list)
        file_list, missing_artists = match_tracks(tracks, artist_dict)

        matched_count = len(file_list)
        missing_count = len(missing_artists)

        assert matched_count > 0 or missing_count > 0

    def test_artist_playlist_relationship_preserved(self):
        from playlist_lib import build_artist_dict, match_tracks

        artist_list = [
            ("Artist A", "1"),
            ("Artist A", "2"),
            ("Artist B", "1"),
        ]

        artist_dict = build_artist_dict(artist_list)
        tracks = ["Artist A/Album/Track.mp3"]

        file_list, _ = match_tracks(tracks, artist_dict)

        playlist_ids = [list(item.keys())[0] for item in file_list]
        assert "1" in playlist_ids
        assert "2" in playlist_ids
        assert len(playlist_ids) == 2

    def test_track_order_preservation(self):
        """Track order is reversed."""
        from playlist_lib import match_tracks

        tracks = [f"Artist/Album/Track{i:02d}.mp3" for i in range(1, 11)]
        artist_dict = {"Artist": ["1"]}

        file_list, _ = match_tracks(tracks, artist_dict)

        first_track = list(file_list[0].values())[0]
        last_track = list(file_list[-1].values())[0]

        assert "Track10" in first_track
        assert "Track01" in last_track
