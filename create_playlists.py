from pathlib import Path
from playlist_lib import (
    read_files,
    build_artist_dict,
    match_tracks,
    match_missing_tracks,
    build_playlists,
    export_playlists,
    export_raw_playlists,
)

LOCAL_BASEPATH = "/home/david/nfs/WDC14/Musique/"
BASEPATH = "/music/"

FOLDER_PATH = "files"
FAVORITE_TRACKS_FILE_NAME = f"{FOLDER_PATH}/00_dbeley-favorite-tracks.txt"
PLAYLISTS_FILE_NAME = f"{FOLDER_PATH}/01_playlists.csv"
ARTISTS_FILE_NAME = f"{FOLDER_PATH}/02_artists.csv"
ARTISTS_NOT_FOUND_FILE_NAME = f"{FOLDER_PATH}/03_artists_NOT-FOUND.csv"
RESULT_MPLAYLIST_FILE_NAME = f"{FOLDER_PATH}/04_result-mplaylist.csv"
RESULT_MPLAYLIST_MISSING_FILE_NAME = f"{FOLDER_PATH}/05_result-mplaylist-missing.csv"
FIX_MISSING_TRACKS_FILE_NAME = f"{FOLDER_PATH}/06_fix-missing-tracks.csv"
FIX_MISSING_TRACKS_NOT_FOUND_FILE_NAME = (
    f"{FOLDER_PATH}/07_fix-missing-tracks_NOT-FOUND.csv"
)

Path(ARTISTS_NOT_FOUND_FILE_NAME).unlink(missing_ok=True)
Path(FIX_MISSING_TRACKS_NOT_FOUND_FILE_NAME).unlink(missing_ok=True)


(
    raw_tracks,
    tracks,
    missing_tracks,
    playlist_dict,
    artist_list,
    missing_dict,
) = read_files(
    FAVORITE_TRACKS_FILE_NAME,
    PLAYLISTS_FILE_NAME,
    ARTISTS_FILE_NAME,
    RESULT_MPLAYLIST_FILE_NAME,
    RESULT_MPLAYLIST_MISSING_FILE_NAME,
    FIX_MISSING_TRACKS_FILE_NAME,
)

artist_dict = build_artist_dict(artist_list)
file_list, missing_artists = match_tracks(tracks, artist_dict)
raw_track_list, raw_missing_artists = match_tracks(raw_tracks, artist_dict, sep=" - ")
missing_file_list, list_missing_paths, missing_artists2 = match_missing_tracks(
    missing_tracks, missing_dict, artist_dict, LOCAL_BASEPATH
)
file_list = missing_file_list + file_list
missing_artists = missing_artists + missing_artists2

if len(missing_artists) > 0:
    missing_artists = set(missing_artists)
    for missing_artist in missing_artists:
        print(f"{missing_artist} is missing.")
    print(f"{len(missing_artists)} artists missing!")

    with open(ARTISTS_NOT_FOUND_FILE_NAME, "w") as f:
        f.write("\n".join(missing_artists))

if len(list_missing_paths) > 0:
    missing_paths = set(list_missing_paths)
    for missing_path in sorted(missing_paths):
        print(f"{missing_path} is missing.")
    print(f"{len(missing_paths)} paths missing!")

    with open(FIX_MISSING_TRACKS_NOT_FOUND_FILE_NAME, "w") as f:
        f.write("\n".join(missing_paths))

nb_missing_artists = len(set(missing_artists))
nb_missing_paths = len(list_missing_paths)

final_dict = build_playlists(file_list, playlist_dict)
raw_final_dict = build_playlists(raw_track_list + missing_file_list, playlist_dict)

export_playlists("playlists", BASEPATH, final_dict)
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
