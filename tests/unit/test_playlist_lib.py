import pytest
from playlist_lib import (
    read_files,
    build_artist_dict,
    match_tracks,
    match_missing_tracks,
    build_playlists,
    export_playlists,
    export_raw_playlists,
)


@pytest.mark.unit
class TestReadFiles:
    def test_read_basic_files(
        self, sample_favorite_tracks, sample_playlists, sample_artists
    ):
        raw_tracks, tracks, missing_tracks, playlist_dict, artist_list, missing_dict = (
            read_files(sample_favorite_tracks, sample_playlists, sample_artists)
        )

        assert len(raw_tracks) == 4
        assert "Artist One - Track One" in raw_tracks
        assert len(tracks) == 0
        assert len(missing_tracks) == 0
        assert playlist_dict == {"1": "Rock", "2": "Pop", "3": "Jazz"}
        assert len(artist_list) == 4
        assert ("Artist One", "1") in artist_list
        assert missing_dict == {}

    def test_read_all_files(
        self,
        sample_favorite_tracks,
        sample_playlists,
        sample_artists,
        sample_result_mplaylist,
        sample_result_missing,
        sample_fix_missing,
    ):
        raw_tracks, tracks, missing_tracks, playlist_dict, artist_list, missing_dict = (
            read_files(
                sample_favorite_tracks,
                sample_playlists,
                sample_artists,
                sample_result_mplaylist,
                sample_result_missing,
                sample_fix_missing,
            )
        )

        assert len(raw_tracks) == 4
        assert len(tracks) == 4
        assert len(missing_tracks) == 1
        assert "Artist Four - Missing Track" in missing_tracks
        assert len(artist_list) == 4
        assert len(missing_dict) == 1
        assert "Artist Four - Missing Track" in missing_dict

    def test_read_empty_favorite_tracks(
        self, temp_dir, sample_playlists, sample_artists
    ):
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("")

        raw_tracks, _, _, _, _, _ = read_files(
            empty_file, sample_playlists, sample_artists
        )

        assert raw_tracks == []

    def test_read_nonexistent_optional_files(
        self, sample_favorite_tracks, sample_playlists, sample_artists
    ):
        _, tracks, missing_tracks, _, _, missing_dict = read_files(
            sample_favorite_tracks,
            sample_playlists,
            sample_artists,
            "/nonexistent/file1.csv",
            "/nonexistent/file2.csv",
            "/nonexistent/file3.csv",
        )

        assert tracks == []
        assert missing_tracks == []
        assert missing_dict == {}


@pytest.mark.unit
class TestBuildArtistDict:
    def test_single_playlist_per_artist(self):
        artist_list = [("Artist A", "1"), ("Artist B", "2")]
        result = build_artist_dict(artist_list)

        assert result == {"Artist A": ["1"], "Artist B": ["2"]}

    def test_multiple_playlists_per_artist(self):
        artist_list = [
            ("Artist A", "1"),
            ("Artist A", "2"),
            ("Artist B", "1"),
        ]
        result = build_artist_dict(artist_list)

        assert result == {"Artist A": ["1", "2"], "Artist B": ["1"]}

    def test_empty_artist_list(self):
        result = build_artist_dict([])
        assert result == {}

    def test_duplicate_entries(self):
        artist_list = [
            ("Artist A", "1"),
            ("Artist A", "1"),
            ("Artist A", "2"),
        ]
        result = build_artist_dict(artist_list)

        assert result == {"Artist A": ["1", "1", "2"]}


@pytest.mark.unit
class TestMatchTracks:
    def test_match_with_slash_separator(self):
        tracks = [
            "Artist One/Album/Track.mp3",
            "Artist Two/Album/Track.mp3",
        ]
        artist_dict = {"Artist One": ["1"], "Artist Two": ["2"]}

        file_list, missing_artists = match_tracks(tracks, artist_dict)

        assert len(file_list) == 2
        assert {"1": "Artist One/Album/Track.mp3"} in file_list
        assert {"2": "Artist Two/Album/Track.mp3"} in file_list
        assert missing_artists == []

    def test_match_with_dash_separator(self):
        tracks = [
            "Artist One - Track Name",
            "Artist Two - Track Name",
        ]
        artist_dict = {"Artist One": ["1"], "Artist Two": ["2"]}

        file_list, missing_artists = match_tracks(tracks, artist_dict, sep=" - ")

        assert len(file_list) == 2
        assert {"1": "Artist One - Track Name"} in file_list
        assert {"2": "Artist Two - Track Name"} in file_list
        assert missing_artists == []

    def test_match_missing_artists(self):
        tracks = [
            "Known Artist/Album/Track.mp3",
            "Unknown Artist/Album/Track.mp3",
        ]
        artist_dict = {"Known Artist": ["1"]}

        file_list, missing_artists = match_tracks(tracks, artist_dict)

        assert len(file_list) == 1
        assert {"1": "Known Artist/Album/Track.mp3"} in file_list
        assert "Unknown Artist" in missing_artists

    def test_match_artist_multiple_playlists(self):
        tracks = ["Artist One/Album/Track.mp3"]
        artist_dict = {"Artist One": ["1", "2", "3"]}

        file_list, missing_artists = match_tracks(tracks, artist_dict)

        assert len(file_list) == 3
        assert {"1": "Artist One/Album/Track.mp3"} in file_list
        assert {"2": "Artist One/Album/Track.mp3"} in file_list
        assert {"3": "Artist One/Album/Track.mp3"} in file_list
        assert missing_artists == []

    def test_reverse_order(self):
        tracks = [
            "Artist/Album/Track1.mp3",
            "Artist/Album/Track2.mp3",
            "Artist/Album/Track3.mp3",
        ]
        artist_dict = {"Artist": ["1"]}

        file_list, _ = match_tracks(tracks, artist_dict)

        assert file_list[0] == {"1": "Artist/Album/Track3.mp3"}
        assert file_list[1] == {"1": "Artist/Album/Track2.mp3"}
        assert file_list[2] == {"1": "Artist/Album/Track1.mp3"}

    def test_empty_tracks(self):
        file_list, missing_artists = match_tracks([], {"Artist": ["1"]})

        assert file_list == []
        assert missing_artists == []


@pytest.mark.unit
class TestMatchMissingTracks:
    def test_match_existing_file(self, temp_dir):
        # Create a test file
        test_file = temp_dir / "test_track.mp3"
        test_file.write_text("test")

        missing_tracks = ["Artist One - Track"]
        missing_dict = {"Artist One - Track": str(test_file)}
        artist_dict = {"Artist One": ["1"]}

        missing_file_list, list_missing_paths, missing_artists = match_missing_tracks(
            missing_tracks, missing_dict, artist_dict, ""
        )

        assert len(missing_file_list) == 1
        assert {"1": str(test_file)} in missing_file_list
        assert list_missing_paths == []
        assert missing_artists == []

    def test_match_nonexistent_file(self, capsys):
        missing_tracks = ["Artist One - Track"]
        missing_dict = {"Artist One - Track": "/nonexistent/file.mp3"}
        artist_dict = {"Artist One": ["1"]}

        missing_file_list, list_missing_paths, missing_artists = match_missing_tracks(
            missing_tracks, missing_dict, artist_dict, ""
        )

        assert missing_file_list == []
        assert list_missing_paths == []
        assert missing_artists == []

        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "doesn't seem to exist" in captured.out

    def test_basepath_replacement(self, temp_dir):
        test_file = temp_dir / "music" / "track.mp3"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("test")

        missing_tracks = ["Artist - Track"]
        missing_dict = {"Artist - Track": str(test_file)}
        artist_dict = {"Artist": ["1"]}
        local_basepath = str(temp_dir) + "/"

        missing_file_list, _, _ = match_missing_tracks(
            missing_tracks, missing_dict, artist_dict, local_basepath
        )

        assert len(missing_file_list) == 1
        path = list(missing_file_list[0].values())[0]
        assert path == "music/track.mp3"

    def test_track_not_in_missing_dict(self):
        missing_tracks = ["Artist - Unknown Track"]
        missing_dict = {}
        artist_dict = {"Artist": ["1"]}

        missing_file_list, list_missing_paths, missing_artists = match_missing_tracks(
            missing_tracks, missing_dict, artist_dict, ""
        )

        assert missing_file_list == []
        assert "Artist - Unknown Track" in list_missing_paths
        assert missing_artists == []

    def test_artist_not_in_artist_dict(self, temp_dir):
        test_file = temp_dir / "track.mp3"
        test_file.write_text("test")

        missing_tracks = ["Unknown Artist - Track"]
        missing_dict = {"Unknown Artist - Track": str(test_file)}
        artist_dict = {"Known Artist": ["1"]}

        missing_file_list, list_missing_paths, missing_artists = match_missing_tracks(
            missing_tracks, missing_dict, artist_dict, ""
        )

        assert missing_file_list == []
        assert list_missing_paths == []
        assert "Unknown Artist" in missing_artists


@pytest.mark.unit
class TestBuildPlaylists:
    def test_basic_playlist_building(self):
        file_list = [
            {"1": "track1.mp3"},
            {"2": "track2.mp3"},
            {"1": "track3.mp3"},
        ]
        playlist_dict = {"1": "Rock", "2": "Pop"}

        result = build_playlists(file_list, playlist_dict)

        assert "1_Rock" in result
        assert "2_Pop" in result
        assert result["1_Rock"] == ["track1.mp3", "track3.mp3"]
        assert result["2_Pop"] == ["track2.mp3"]

    def test_playlist_id_padding(self):
        file_list = [
            {"1": "track1.mp3"},
            {"10": "track2.mp3"},
        ]
        playlist_dict = {"1": "Rock", "10": "Jazz"}

        result = build_playlists(file_list, playlist_dict)

        assert "01_Rock" in result
        assert "10_Jazz" in result

    def test_playlist_not_in_dict(self, capsys):
        file_list = [{"99": "track.mp3"}]
        playlist_dict = {"1": "Rock"}

        result = build_playlists(file_list, playlist_dict)

        assert "99_" not in result
        assert result == {}

        captured = capsys.readouterr()
        assert "not in playlist dict" in captured.out

    def test_empty_file_list(self):
        result = build_playlists([], {"1": "Rock"})
        assert result == {}

    def test_playlist_name_with_slash(self):
        file_list = [{"1": "track.mp3"}]
        playlist_dict = {"1": "Rock/Metal"}

        result = build_playlists(file_list, playlist_dict)

        assert "1_Rock/Metal" in result


@pytest.mark.unit
class TestExportPlaylists:
    def test_export_basic_playlist(self, temp_dir):
        folder = temp_dir / "playlists"
        final_dict = {
            "1_Rock": ["track1.mp3", "track2.mp3"],
            "2_Pop": ["track3.mp3"],
        }

        export_playlists(str(folder), "/music/", final_dict)

        rock_file = folder / "1_Rock.m3u"
        pop_file = folder / "2_Pop.m3u"

        assert rock_file.exists()
        assert pop_file.exists()

        rock_content = rock_file.read_text()
        assert rock_content == "/music/track1.mp3\n/music/track2.mp3"

        pop_content = pop_file.read_text()
        assert pop_content == "/music/track3.mp3"

    def test_export_without_basepath(self, temp_dir):
        folder = temp_dir / "playlists"
        final_dict = {"1_Rock": ["track1.mp3"]}

        export_playlists(str(folder), "", final_dict)

        content = (folder / "1_Rock.m3u").read_text()
        assert content == "track1.mp3"

    def test_export_creates_directory(self, temp_dir):
        folder = temp_dir / "new" / "playlists"
        final_dict = {"1_Rock": ["track.mp3"]}

        export_playlists(str(folder), "", final_dict)

        assert folder.exists()

    def test_export_slash_in_name(self, temp_dir):
        folder = temp_dir / "playlists"
        final_dict = {"1_Rock/Metal": ["track.mp3"]}

        export_playlists(str(folder), "", final_dict)

        assert (folder / "1_Rock-Metal.m3u").exists()

    def test_export_empty_playlist(self, temp_dir):
        folder = temp_dir / "playlists"
        final_dict = {"1_Rock": []}

        export_playlists(str(folder), "/music/", final_dict)

        content = (folder / "1_Rock.m3u").read_text()
        assert content == ""


@pytest.mark.unit
class TestExportRawPlaylists:
    def test_export_raw_playlist(self, temp_dir):
        folder = temp_dir / "raw_playlists"
        final_dict = {
            "1_Rock": ["Artist/Album/track1.mp3", "Artist/Album/track2.mp3"],
        }

        export_raw_playlists(final_dict, str(folder))

        rock_file = folder / "1_Rock.txt"
        assert rock_file.exists()

        content = rock_file.read_text()
        assert content == "Artist/Album/track1.mp3\nArtist/Album/track2.mp3"

    def test_export_raw_with_default_folder(self, temp_dir, monkeypatch):
        monkeypatch.chdir(temp_dir)

        final_dict = {"1_Rock": ["track.mp3"]}
        export_raw_playlists(final_dict)

        assert (temp_dir / "raw_playlists" / "1_Rock.txt").exists()

    def test_export_raw_slash_in_name(self, temp_dir):
        folder = temp_dir / "raw_playlists"
        final_dict = {"1_Rock/Metal": ["track.mp3"]}

        export_raw_playlists(final_dict, str(folder))

        assert (folder / "1_Rock-Metal.txt").exists()
