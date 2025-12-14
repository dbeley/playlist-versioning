from collections import defaultdict
from pathlib import Path


def read_files(
    favorite_tracks_file,
    playlists_file,
    artists_file,
    result_mplaylist_file=None,
    result_mplaylist_missing_file=None,
    fix_missing_tracks_file=None,
):
    # Preserves current behavior: empty lines become empty strings, malformed CSV raises IndexError
    with open(favorite_tracks_file, "r", encoding="utf-8") as f:
        raw_tracks = [x.strip() for x in f.readlines()]

    with open(playlists_file, "r", encoding="utf-8") as f:
        playlist_dict = dict([x.strip().split(";") for x in f.readlines()])

    with open(artists_file, "r", encoding="utf-8") as f:
        artist_list = [
            (x.strip().split(";")[1], x.strip().split(";")[0]) for x in f.readlines()
        ]

    tracks = []
    if result_mplaylist_file and Path(result_mplaylist_file).exists():
        with open(result_mplaylist_file, "r", encoding="utf-8") as f:
            tracks = [x.strip() for x in f.readlines()]

    missing_tracks = []
    if result_mplaylist_missing_file and Path(result_mplaylist_missing_file).exists():
        with open(result_mplaylist_missing_file, "r", encoding="utf-8") as f:
            missing_tracks = [x.strip() for x in f.readlines()]

    missing_dict = {}
    if fix_missing_tracks_file and Path(fix_missing_tracks_file).exists():
        with open(fix_missing_tracks_file, "r", encoding="utf-8") as f:
            missing_dict = dict(
                [
                    (x.strip().split(";")[0], x.strip().split(";")[1])
                    for x in f.readlines()
                ]
            )

    return raw_tracks, tracks, missing_tracks, playlist_dict, artist_list, missing_dict


def build_artist_dict(artist_list):
    artist_dict = {}
    for i in artist_list:
        if i[0] in artist_dict:
            artist_dict[i[0]] += [i[1]]
        else:
            artist_dict[i[0]] = [i[1]]
    return artist_dict


def match_tracks(tracks, artist_dict, sep="/"):
    # Tracks processed in reverse order to have newest tracks at the end
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


def match_missing_tracks(missing_tracks, missing_dict, artist_dict, local_basepath=""):
    list_missing_paths = []
    missing_file_list = []
    missing_artists = []

    for track in missing_tracks:
        if track in missing_dict:
            artist = track.split(" - ")[0]
            path = missing_dict[track].strip()
            my_file = Path(path)

            if not my_file.is_file():
                print(
                    f"WARNING: file {path} doesn't seem to exist for track {track}. Skipping."
                )
            elif artist in artist_dict:
                for i in artist_dict[artist]:
                    missing_file_list.append({i: path.replace(local_basepath, "")})
            else:
                missing_artists.append(artist)
        else:
            list_missing_paths.append(track)

    return missing_file_list, list_missing_paths, missing_artists


def build_playlists(file_list, playlist_dict):
    d = defaultdict(list)
    for i in file_list:
        k, v = list(i.items())[0]
        d[k].append(v)

    condensed_dict = dict(d)
    final_dict = dict()
    max_playlist_id = max([int(x) for x in playlist_dict])

    for k, v in condensed_dict.items():
        if k in playlist_dict:
            final_dict[f"{k.zfill(len(str(max_playlist_id)))}_{playlist_dict[k]}"] = v
        else:
            print(f"Playlist name {k} not in playlist dict.")

    return final_dict


def export_playlists(folder, path, final_dict):
    Path(folder).mkdir(parents=True, exist_ok=True)
    for playlist, tracks in final_dict.items():
        filename = f"{folder}/{playlist.replace('/', '-')}.m3u"
        print(f"Creating {filename}.")
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join([f"{path}{x}" for x in tracks]))


def export_raw_playlists(final_dict, folder="raw_playlists"):
    Path(folder).mkdir(parents=True, exist_ok=True)
    for playlist, tracks in final_dict.items():
        filename = f"{folder}/{playlist.replace('/', '-')}.txt"
        print(f"Creating {filename}.")
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join([x for x in tracks]))
