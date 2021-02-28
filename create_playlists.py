from collections import defaultdict
from pathlib import Path

# prefix or base path
LOCAL_BASEPATH = "/home/david/nfs/Toshiba/Musique/"
BASEPATH = "/music/"

# result of mplaylist.sh
with open("files/01-result_mplaylist.csv", "r") as f:
    tracks = [x.strip() for x in f.readlines()]
with open("files/01-result_mplaylist_missing.csv", "r") as f:
    missing_tracks = [x.strip() for x in f.readlines()]

# artists.csv
with open("files/03-artists.csv", "r") as f:
    dict_genres = dict(
        [(x.strip().split(";")[1], x.strip().split(";")[0]) for x in f.readlines()]
    )

# correspondances.csv
with open("files/02-playlists.csv", "r") as f:
    corr = dict([x.strip().split(";") for x in f.readlines()])

# matching with tracks
with open("files/04-missing_tracks.csv", "r") as f:
    dict_paths = dict(
        [(x.strip().split(";")[0], x.strip().split(";")[1]) for x in f.readlines()]
    )

list_file = []
list_missing_artists = []
for track in tracks:
    artist = track.split("/")[0]
    if artist in dict_genres:
        list_file.append({dict_genres[artist]: track})
    else:
        list_missing_artists.append(artist)

list_missing_paths = []
for track in missing_tracks:
    if track in dict_paths:
        # check file exists
        artist = track.split(" - ")[0]
        path = dict_paths[track]
        my_file = Path(path)
        if not my_file.is_file():
            print(f"WARNING: file {path} doesn't seem to exist for track {track}.")
        elif artist in dict_genres:
            list_file.append({dict_genres[artist]: path.replace(LOCAL_BASEPATH, "")})
        else:
            list_missing_artists.append(artist)
    else:
        list_missing_paths.append(track)

if len(list_missing_artists) > 0:
    missing_artists = set(list_missing_artists)
    for missing_artist in missing_artists:
        print(f"{missing_artist} is missing.")
    print(f"{len(list_missing_artists)} artists missing!")

    with open("files/03-missing_artists.csv", "w") as f:
        f.write("\n".join(missing_artists))

if len(list_missing_paths) > 0:
    missing_paths = set(list_missing_paths)
    for missing_path in sorted(missing_paths):
        print(f"{missing_path} is missing.")
    print(f"{len(list_missing_paths)} paths missing!")

    with open("files/04-missing_tracks_missing.csv", "w") as f:
        f.write("\n".join(missing_paths))

d = defaultdict(list)
for i in list_file:
    k, v = list(i.items())[
        0
    ]  # an alternative to the single-iterating inner loop from the previous solution
    d[k].append(v)

condensed_dict = dict(d)
final_dict = dict()
for k, v in condensed_dict.items():
    if k in corr:
        final_dict[corr[k]] = v
    else:
        print(f"Playlist name {k} not in correspondances.csv.")
# print(final_dict)

# export
for playlist, tracks in final_dict.items():
    # print(playlist)
    filename = f"files/mplaylist_{playlist.replace('/', '-')}.m3u8"
    with open(filename, "w") as f:
        print(f"Creating {filename}.")
        f.write("\n".join([f"{BASEPATH}{x}" for x in tracks]))
