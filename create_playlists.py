from collections import defaultdict
from pathlib import Path

# prefix or base path
LOCAL_BASEPATH = "/home/david/nfs/WDC14/Musique/"
BASEPATH = "/var/music/"

# delete NOT-FOUND files if exists
Path("files/03_artists_NOT-FOUND.csv").unlink(missing_ok=True)
Path("files/04_fix-missing-tracks_NOT-FOUND.csv").unlink(missing_ok=True)


def read_files():
    """
    Returns:
        - raw_tracks: list of tracks
        - tracks: list of files found by mplaylist
        - missing_tracks: list of files not found by mplaylist
        - playlist_dict: list of dict containing playlists (id + name)
        - artist_list: list of dict containing artists (artist name + playlist id)
            Duplicate artist name with different playlist id is supported
        - missing_dict: list of manually matched files
    """
    with open("files/00_dbeley-favorite-tracks.txt", "r") as f:
        raw_tracks = [x.strip() for x in f.readlines()]
    with open("files/01_result-mplaylist.csv", "r") as f:
        tracks = [x.strip() for x in f.readlines()]
    with open("files/01_result-mplaylist-missing.csv", "r") as f:
        missing_tracks = [x.strip() for x in f.readlines()]
    with open("files/02_playlists.csv", "r") as f:
        playlist_dict = dict([x.strip().split(";") for x in f.readlines()])
    with open("files/03_artists.csv", "r") as f:
        artist_list = [
            (x.strip().split(";")[1], x.strip().split(";")[0]) for x in f.readlines()
        ]
    with open("files/04_fix-missing-tracks.csv", "r") as f:
        missing_dict = dict(
            [(x.strip().split(";")[0], x.strip().split(";")[1]) for x in f.readlines()]
        )
    return raw_tracks, tracks, missing_tracks, playlist_dict, artist_list, missing_dict


def build_artist_dict(artist_list):
    """
    Returns a dict where the key is the artist name,
        and the value is a list of playlist ids.
    """
    artist_dict = {}
    for i in artist_list:
        if i[0] in artist_dict:
            artist_dict[i[0]] += [i[1]]
        else:
            artist_dict[i[0]] = [i[1]]
    return artist_dict


def match_tracks(tracks, artist_dict, sep="/"):
    """
    Returns:
        - file_list: list of dict where
            - key: playlist id
            - value: file
        - missing_artists: list of artists unmatched
    The tracks are looped in reverse in order to have the newest tracks at the end
    """
    file_list = []
    missing_artists = []
    for track in reversed(tracks):
        artist = track.split(sep)[0].strip()
        if artist in artist_dict:
            for playlist_id in artist_dict[artist]:
                file_list.append({playlist_id: track})
        else:
            missing_artists.append(artist)

    return file_list, missing_artists


def match_missing_tracks(missing_tracks, missing_dict, artist_dict):
    list_missing_paths = []
    missing_file_list = []
    missing_artists = []
    for track in missing_tracks:
        if track in missing_dict:
            # check file exists
            artist = track.split(" - ")[0]
            path = missing_dict[track].strip()
            my_file = Path(path)
            if not my_file.is_file():
                # if any(x in str(my_file) for x in ["MISSING", "DUPLICATE"]):
                print(
                    f"WARNING: file {path} doesn't seem to exist for track {track}. Skipping."
                )
            elif artist in artist_dict:
                for i in artist_dict[artist]:
                    missing_file_list.append({i: path.replace(LOCAL_BASEPATH, "")})
            else:
                missing_artists.append(artist)
        else:
            list_missing_paths.append(track)
    return missing_file_list, list_missing_paths, missing_artists


def build_playlists(file_list, playlist_dict):
    d = defaultdict(list)
    for i in file_list:
        k, v = list(i.items())[
            0
        ]  # an alternative to the single-iterating inner loop from the previous solution
        d[k].append(v)

    condensed_dict = dict(d)
    final_dict = dict()
    max_playlist_id = max([int(x) for x in playlist_dict])
    for k, v in condensed_dict.items():
        if k in playlist_dict:
            final_dict[f"{k.zfill(len(str(max_playlist_id)))}_{playlist_dict[k]}"] = v
        else:
            print(f"Playlist name {k} not in 02_playlists.csv.")
    return final_dict


def export_playlists(final_dict):
    Path("playlists").mkdir(parents=True, exist_ok=True)
    for playlist, tracks in final_dict.items():
        filename = f"playlists/{playlist.replace('/', '-')}.m3u8"
        print(f"Creating {filename}.")
        with open(filename, "w") as f:
            f.write("\n".join([f"{BASEPATH}{x}" for x in tracks]))


def export_raw_playlists(final_dict):
    Path("playlists").mkdir(parents=True, exist_ok=True)
    for playlist, tracks in final_dict.items():
        filename = f"raw_playlists/{playlist.replace('/', '-')}.txt"
        print(f"Creating {filename}.")
        with open(filename, "w") as f:
            f.write("\n".join([x for x in tracks]))


(
    raw_tracks,
    tracks,
    missing_tracks,
    playlist_dict,
    artist_list,
    missing_dict,
) = read_files()

artist_dict = build_artist_dict(artist_list)
file_list, missing_artists = match_tracks(tracks, artist_dict)
raw_track_list, raw_missing_artists = match_tracks(raw_tracks, artist_dict, sep=" - ")
missing_file_list, list_missing_paths, missing_artists2 = match_missing_tracks(
    missing_tracks, missing_dict, artist_dict
)
file_list = missing_file_list + file_list
missing_artists = missing_artists + missing_artists2

if len(missing_artists) > 0:
    missing_artists = set(missing_artists)
    for missing_artist in missing_artists:
        print(f"{missing_artist} is missing.")
    print(f"{len(missing_artists)} artists missing!")

    with open("files/03_artists_NOT-FOUND.csv", "w") as f:
        f.write("\n".join(missing_artists))

if len(list_missing_paths) > 0:
    missing_paths = set(list_missing_paths)
    for missing_path in sorted(missing_paths):
        print(f"{missing_path} is missing.")
    print(f"{len(missing_paths)} paths missing!")

    with open("files/04_fix-missing-tracks_NOT-FOUND.csv", "w") as f:
        f.write("\n".join(missing_paths))

nb_missing_artists = len(set(missing_artists))
nb_missing_paths = len(list_missing_paths)

final_dict = build_playlists(file_list, playlist_dict)
raw_final_dict = build_playlists(raw_track_list + missing_file_list, playlist_dict)

export_playlists(final_dict)
export_raw_playlists(raw_final_dict)

print(
    f"{nb_missing_artists} artists not found in 03_artists.csv.\n{nb_missing_paths} missing tracks not found in 04_fix-missing-tracks.csv."
)
if nb_missing_artists > 0:
    print("Update 03_artists.csv with the artists in 03_artists_NOT-FOUND.csv.")
if nb_missing_paths > 0:
    print(
        "Update 04-fix_missing_tracks.csv with the paths in 04_fix-missing-tracks_NOT-FOUND.csv."
    )
if nb_missing_artists == 0 and nb_missing_paths == 0:
    print(
        "You're all set, all your playlists were successfully created in the playlists folder!"
    )
