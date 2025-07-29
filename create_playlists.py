"""Generate playlists based on favorite tracks and manual mappings."""

from collections import defaultdict
from pathlib import Path
import csv

# prefix or base path
LOCAL_BASEPATH = "/home/david/nfs/WDC14/Musique/"
BASEPATH = "/music/"

FOLDER_PATH = "files"
# Favorite tracks
FAVORITE_TRACKS_FILE_NAME = f"{FOLDER_PATH}/00_dbeley-favorite-tracks.txt"
# Playlists matching
PLAYLISTS_FILE_NAME = f"{FOLDER_PATH}/01_playlists.csv"
# Artists matching
ARTISTS_FILE_NAME = f"{FOLDER_PATH}/02_artists.csv"
# Artists not found in the previous file, this file should be empty
ARTISTS_NOT_FOUND_FILE_NAME = f"{FOLDER_PATH}/03_artists_NOT-FOUND.csv"
# Tracks found in MPD
RESULT_MPLAYLIST_FILE_NAME = f"{FOLDER_PATH}/04_result-mplaylist.csv"
# Tracks missing in MPD
RESULT_MPLAYLIST_MISSING_FILE_NAME = f"{FOLDER_PATH}/05_result-mplaylist-missing.csv"
# Missing tracks matching
FIX_MISSING_TRACKS_FILE_NAME = f"{FOLDER_PATH}/06_fix-missing-tracks.csv"
# Missing tracks not found in the previous file, this file should be empty
FIX_MISSING_TRACKS_NOT_FOUND_FILE_NAME = f"{FOLDER_PATH}/07_fix-missing-tracks_NOT-FOUND.csv"

# delete NOT-FOUND files if exists
Path(ARTISTS_NOT_FOUND_FILE_NAME).unlink(missing_ok=True)
Path(FIX_MISSING_TRACKS_NOT_FOUND_FILE_NAME).unlink(missing_ok=True)

def read_lines(path: str) -> list[str]:
    """Return a list of non empty stripped lines from *path* if it exists."""
    if not Path(path).exists():
        return []
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def read_csv_pairs(path: str) -> list[tuple[str, str]]:
    """Return list of tuples from a ``;`` separated csv file."""
    if not Path(path).exists():
        return []
    with open(path, newline="") as f:
        return [tuple(row) for row in csv.reader(f, delimiter=";") if len(row) == 2]


def read_files():
    """Load raw tracks, playlist definitions and manual mappings."""

    raw_tracks = read_lines(FAVORITE_TRACKS_FILE_NAME)
    playlist_dict = {pid: name for pid, name in read_csv_pairs(PLAYLISTS_FILE_NAME)}
    artist_list = [(artist, pid) for pid, artist in read_csv_pairs(ARTISTS_FILE_NAME)]
    tracks = read_lines(RESULT_MPLAYLIST_FILE_NAME)
    missing_tracks = read_lines(RESULT_MPLAYLIST_MISSING_FILE_NAME)
    missing_dict = {track: path for track, path in read_csv_pairs(FIX_MISSING_TRACKS_FILE_NAME)}

    return raw_tracks, tracks, missing_tracks, playlist_dict, artist_list, missing_dict


def build_artist_dict(artist_list):
    """Return a mapping of artist name to a list of playlist ids."""

    artist_dict: dict[str, list[str]] = defaultdict(list)
    for artist, playlist_id in artist_list:
        artist_dict[artist].append(playlist_id)
    return artist_dict


def match_tracks(tracks: list[str], artist_dict: dict[str, list[str]], sep: str = "/"):
    """Return mapping playlist_id -> tracks and list of unknown artists."""

    file_map: defaultdict[str, list[str]] = defaultdict(list)
    missing_artists: list[str] = []

    for track in reversed(tracks):  # newest tracks last
        artist = track.split(sep)[0].strip()
        if artist in artist_dict:
            for playlist_id in artist_dict[artist]:
                file_map[playlist_id].append(track)
        else:
            missing_artists.append(artist)

    return file_map, missing_artists


def match_missing_tracks(
    missing_tracks: list[str],
    missing_dict: dict[str, str],
    artist_dict: dict[str, list[str]],
) -> tuple[defaultdict[str, list[str]], list[str], list[str]]:
    """Handle tracks not found by MPD using the manual mapping file."""

    list_missing_paths: list[str] = []
    file_map: defaultdict[str, list[str]] = defaultdict(list)
    missing_artists: list[str] = []

    for track in missing_tracks:
        if track not in missing_dict:
            list_missing_paths.append(track)
            continue

        artist = track.split(" - ")[0]
        path = missing_dict[track].strip()
        if not Path(path).is_file():
            print(
                f"WARNING: file {path} doesn't seem to exist for track {track}. Skipping."
            )
            continue
        path = path.replace(LOCAL_BASEPATH, "")

        if artist in artist_dict:
            for pid in artist_dict[artist]:
                file_map[pid].append(path)
        else:
            missing_artists.append(artist)

    return file_map, list_missing_paths, missing_artists


def build_playlists(file_map: dict[str, list[str]], playlist_dict: dict[str, str]):
    """Return final playlist name -> tracks mapping."""

    final_dict: dict[str, list[str]] = {}
    if not playlist_dict:
        return final_dict

    max_id_len = len(str(max(int(x) for x in playlist_dict)))

    for pid, tracks in file_map.items():
        if pid in playlist_dict:
            name = f"{str(pid).zfill(max_id_len)}_{playlist_dict[pid]}"
            final_dict[name] = tracks
        else:
            print(f"Playlist name {pid} not in {PLAYLISTS_FILE_NAME}.")

    return final_dict


def export_playlists(folder: str, path: str, final_dict: dict[str, list[str]]):
    """Write ``.m3u`` playlist files in *folder*."""

    Path(folder).mkdir(parents=True, exist_ok=True)
    for playlist, tracks in final_dict.items():
        filename = f"{folder}/{playlist.replace('/', '-')}.m3u"
        print(f"Creating {filename}.")
        with open(filename, "w") as f:
            f.write("\n".join(f"{path}{x}" for x in tracks))


def export_raw_playlists(final_dict: dict[str, list[str]]):
    """Write simple text playlists without base path."""

    Path("raw_playlists").mkdir(parents=True, exist_ok=True)
    for playlist, tracks in final_dict.items():
        filename = f"raw_playlists/{playlist.replace('/', '-')}.txt"
        print(f"Creating {filename}.")
        with open(filename, "w") as f:
            f.write("\n".join(tracks))




def main() -> None:
    raw_tracks, tracks, missing_tracks, playlist_dict, artist_list, missing_dict = read_files()

    artist_dict = build_artist_dict(artist_list)
    file_map, missing_artists = match_tracks(tracks, artist_dict)
    raw_file_map, raw_missing_artists = match_tracks(raw_tracks, artist_dict, sep=" - ")
    missing_file_map, list_missing_paths, missing_artists2 = match_missing_tracks(
        missing_tracks, missing_dict, artist_dict
    )

    for pid, lst in missing_file_map.items():
        file_map[pid].extend(lst)
        raw_file_map[pid].extend(lst)

    missing_artists += raw_missing_artists + missing_artists2

    if missing_artists:
        missing_artists = set(missing_artists)
        for missing_artist in missing_artists:
            print(f"{missing_artist} is missing.")
        print(f"{len(missing_artists)} artists missing!")

        with open(ARTISTS_NOT_FOUND_FILE_NAME, "w") as f:
            f.write("\n".join(missing_artists))

    if list_missing_paths:
        missing_paths = set(list_missing_paths)
        for missing_path in sorted(missing_paths):
            print(f"{missing_path} is missing.")
        print(f"{len(missing_paths)} paths missing!")

        with open(FIX_MISSING_TRACKS_NOT_FOUND_FILE_NAME, "w") as f:
            f.write("\n".join(missing_paths))

    nb_missing_artists = len(set(missing_artists))
    nb_missing_paths = len(list_missing_paths)

    final_dict = build_playlists(file_map, playlist_dict)
    raw_final_dict = build_playlists(raw_file_map, playlist_dict)

# Playlists with basepath
    export_playlists("playlists", BASEPATH, final_dict)
    # Playlists without basepath, for example to be used with MPD
    export_playlists("mpd_playlists", "", final_dict)
    export_raw_playlists(raw_final_dict)

    print(
        f"{nb_missing_artists} artists not found in {ARTISTS_FILE_NAME}.\n{nb_missing_paths} missing tracks not found in {FIX_MISSING_TRACKS_FILE_NAME}."
    )
    if nb_missing_artists > 0:
        print(
            f"Update {ARTISTS_FILE_NAME} with the artists in {ARTISTS_NOT_FOUND_FILE_NAME}."
        )
    if nb_missing_paths > 0:
        print(
            f"Update {FIX_MISSING_TRACKS_FILE_NAME} with the paths in {FIX_MISSING_TRACKS_NOT_FOUND_FILE_NAME}."
        )
    if nb_missing_artists == 0 and nb_missing_paths == 0:
        print(
            "You're all set, all your playlists were successfully created in the playlists folder!"
        )


if __name__ == "__main__":
    main()
