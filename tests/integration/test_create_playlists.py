"""
Integration tests for the create_playlists script.
Tests file I/O and integration between components.
"""

import pytest


@pytest.mark.integration
class TestCreatePlaylistsIntegration:
    def test_full_workflow_with_sample_data(self, test_files_dir, temp_dir):
        from playlist_lib import (
            read_files,
            build_artist_dict,
            match_tracks,
            build_playlists,
            export_playlists,
        )

        files_dir = test_files_dir / "files"

        raw_tracks, tracks, missing_tracks, playlist_dict, artist_list, missing_dict = (
            read_files(
                files_dir / "00_favorite-tracks.txt",
                files_dir / "01_playlists.csv",
                files_dir / "02_artists.csv",
                files_dir / "04_result-mplaylist.csv",
                files_dir / "05_result-mplaylist-missing.csv",
                files_dir / "06_fix-missing-tracks.csv",
            )
        )

        artist_dict = build_artist_dict(artist_list)
        file_list, missing_artists = match_tracks(tracks, artist_dict)
        final_dict = build_playlists(file_list, playlist_dict)

        playlists_dir = temp_dir / "playlists"
        export_playlists(str(playlists_dir), "/music/", final_dict)

        assert playlists_dir.exists()
        assert len(list(playlists_dir.glob("*.m3u"))) > 0

        rock_playlist = playlists_dir / "1_Rock.m3u"
        if rock_playlist.exists():
            content = rock_playlist.read_text()
            assert "/music/" in content
            assert ".mp3" in content or ".flac" in content or ".opus" in content

    def test_read_write_cycle(self, test_files_dir, temp_dir):
        from playlist_lib import read_files, export_playlists, build_playlists

        files_dir = test_files_dir / "files"

        _, tracks, _, playlist_dict, artist_list, _ = read_files(
            files_dir / "00_favorite-tracks.txt",
            files_dir / "01_playlists.csv",
            files_dir / "02_artists.csv",
            files_dir / "04_result-mplaylist.csv",
        )

        file_list = [{"1": track} for track in tracks]
        final_dict = build_playlists(file_list, playlist_dict)
        output_dir = temp_dir / "output"
        export_playlists(str(output_dir), "", final_dict)

        assert output_dir.exists()
        playlist_files = list(output_dir.glob("*.m3u"))
        assert len(playlist_files) > 0

        for playlist_file in playlist_files:
            content = playlist_file.read_text()
            lines = [line for line in content.split("\n") if line.strip()]
            assert len(lines) > 0

    def test_missing_tracks_workflow(self, test_files_dir, temp_dir):
        from playlist_lib import (
            read_files,
            build_artist_dict,
            match_missing_tracks,
        )

        files_dir = test_files_dir / "files"

        music_file = temp_dir / "music" / "Artist Four" / "Track.mp3"
        music_file.parent.mkdir(parents=True, exist_ok=True)
        music_file.write_text("test")

        fix_file = files_dir / "06_fix-missing-tracks.csv"
        fix_file.write_text(f"Artist Four - Missing Track;{music_file}")

        _, _, missing_tracks, _, artist_list, missing_dict = read_files(
            files_dir / "00_favorite-tracks.txt",
            files_dir / "01_playlists.csv",
            files_dir / "02_artists.csv",
            None,
            files_dir / "05_result-mplaylist-missing.csv",
            fix_file,
        )

        artist_list.append(("Artist Four", "3"))
        artist_dict = build_artist_dict(artist_list)

        missing_file_list, list_missing_paths, missing_artists = match_missing_tracks(
            missing_tracks, missing_dict, artist_dict, str(temp_dir) + "/"
        )

        assert len(missing_file_list) > 0
        assert len(list_missing_paths) == 0
        assert len(missing_artists) == 0

    def test_directory_creation(self, temp_dir):
        from playlist_lib import export_playlists, export_raw_playlists

        final_dict = {"1_Test": ["track1.mp3", "track2.mp3"]}

        playlists_dir = temp_dir / "new" / "playlists"
        assert not playlists_dir.exists()

        export_playlists(str(playlists_dir), "/music/", final_dict)
        assert playlists_dir.exists()
        assert (playlists_dir / "1_Test.m3u").exists()

        raw_dir = temp_dir / "new" / "raw_playlists"
        assert not raw_dir.exists()

        export_raw_playlists(final_dict, str(raw_dir))
        assert raw_dir.exists()
        assert (raw_dir / "1_Test.txt").exists()

    def test_file_content_correctness(self, test_files_dir, temp_dir):
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
        basepath = "/test/music/"
        export_playlists(str(output_dir), basepath, final_dict)

        for playlist_file in output_dir.glob("*.m3u"):
            content = playlist_file.read_text()
            for line in content.split("\n"):
                if line.strip():
                    assert line.startswith(basepath)


@pytest.mark.integration
class TestFileFormats:
    def test_csv_parsing(self, temp_dir):
        from playlist_lib import read_files

        files_dir = temp_dir / "files"
        files_dir.mkdir()

        (files_dir / "tracks.txt").write_text("Artist - Track\n")
        (files_dir / "playlists.csv").write_text("1;Test Playlist\n2;Another\n")
        (files_dir / "artists.csv").write_text("1;Artist\n")

        _, _, _, playlist_dict, artist_list, _ = read_files(
            files_dir / "tracks.txt",
            files_dir / "playlists.csv",
            files_dir / "artists.csv",
        )

        assert playlist_dict == {"1": "Test Playlist", "2": "Another"}
        assert artist_list == [("Artist", "1")]

    def test_m3u_format(self, temp_dir):
        from playlist_lib import export_playlists

        final_dict = {"1_Playlist": ["track1.mp3", "track2.mp3", "track3.mp3"]}

        export_playlists(str(temp_dir), "/music/", final_dict)

        content = (temp_dir / "1_Playlist.m3u").read_text()
        lines = content.split("\n")

        assert len(lines) == 3
        assert lines[0] == "/music/track1.mp3"
        assert lines[1] == "/music/track2.mp3"
        assert lines[2] == "/music/track3.mp3"

    def test_special_characters_in_filenames(self, temp_dir):
        from playlist_lib import export_playlists

        final_dict = {"1_Rock/Metal": ["Artist/Album/Track.mp3"]}

        export_playlists(str(temp_dir), "", final_dict)

        assert (temp_dir / "1_Rock-Metal.m3u").exists()
        assert not (temp_dir / "1_Rock/Metal.m3u").exists()


@pytest.mark.integration
class TestErrorHandling:
    def test_missing_required_files(self, temp_dir):
        from playlist_lib import read_files

        with pytest.raises(FileNotFoundError):
            read_files(
                temp_dir / "nonexistent.txt",
                temp_dir / "nonexistent.csv",
                temp_dir / "nonexistent.csv",
            )

    def test_empty_playlist_dict(self):
        """Captures current behavior: raises ValueError on empty playlist_dict."""
        from playlist_lib import build_playlists

        file_list = [{"1": "track.mp3"}]

        with pytest.raises(ValueError, match="max\\(\\).*empty"):
            build_playlists(file_list, {})

    def test_malformed_csv_data(self, temp_dir):
        from playlist_lib import read_files

        files_dir = temp_dir / "files"
        files_dir.mkdir()

        (files_dir / "tracks.txt").write_text("Artist - Track\n")
        (files_dir / "playlists.csv").write_text("1;Playlist\n")
        (files_dir / "artists.csv").write_text("BadLine\n")

        with pytest.raises(IndexError):
            read_files(
                files_dir / "tracks.txt",
                files_dir / "playlists.csv",
                files_dir / "artists.csv",
            )
