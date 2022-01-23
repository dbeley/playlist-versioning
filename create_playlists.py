from collections import defaultdict
from pathlib import Path

# prefix or base path
LOCAL_BASEPATH = "/home/david/nfs/WDC14/Musique/"
BASEPATH = "/var/music/"

# result of mplaylist.sh
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

artist_dict = dict()
for i in artist_list:
    if i[0] in artist_dict:
        artist_dict[i[0]] += [i[1]]
    else:
        artist_dict[i[0]] = [i[1]]

# matching with tracks
with open("files/04_fix-missing-tracks.csv", "r") as f:
    missing_dict = dict(
        [(x.strip().split(";")[0], x.strip().split(";")[1]) for x in f.readlines()]
    )

# delete NOT_FOUND files if exists
Path("files/03_artists_NOT_FOUND.csv").unlink(missing_ok=True)
Path("files/04_fix-missing-tracks_NOT_FOUND.csv").unlink(missing_ok=True)

file_list = []
missing_artists = []
for track in tracks:
    artist = track.split("/")[0]
    if artist in artist_dict:
        for i in artist_dict[artist]:
            file_list.append({i: track})
    else:
        missing_artists.append(artist)

list_missing_paths = []
for track in missing_tracks:
    if track in missing_dict:
        # check file exists
        artist = track.split(" - ")[0]
        path = missing_dict[track]
        my_file = Path(path)
        if not my_file.is_file():
            # if any(x in str(my_file) for x in ["MISSING", "DUPLICATE"]):
            print(
                f"WARNING: file {path} doesn't seem to exist for track {track}. Skipping."
            )
        elif artist in artist_dict:
            for i in artist_dict[artist]:
                file_list.append({i: path.replace(LOCAL_BASEPATH, "")})
        else:
            missing_artists.append(artist)
    else:
        list_missing_paths.append(track)

if len(missing_artists) > 0:
    missing_artists = set(missing_artists)
    for missing_artist in missing_artists:
        print(f"{missing_artist} is missing.")
    print(f"{len(missing_artists)} artists missing!")

    with open("files/03_artists_NOT_FOUND.csv", "w") as f:
        f.write("\n".join(missing_artists))

if len(list_missing_paths) > 0:
    missing_paths = set(list_missing_paths)
    for missing_path in sorted(missing_paths):
        print(f"{missing_path} is missing.")
    print(f"{len(missing_paths)} paths missing!")

    with open("files/04_fix-missing-tracks_NOT_FOUND.csv", "w") as f:
        f.write("\n".join(missing_paths))

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
        print(f"Playlist name {k} not in 02-playlists.csv.")

# export
Path("playlists").mkdir(parents=True, exist_ok=True)
for playlist, tracks in final_dict.items():
    # print(playlist)
    filename = f"playlists/{playlist.replace('/', '-')}.m3u8"
    print(f"Creating {filename}.")
    with open(filename, "w") as f:
        f.write("\n".join([f"{BASEPATH}{x}" for x in tracks]))

print(
    f"{len(set(missing_artists))} artists not found in 03_artists.csv.\n{len(list_missing_paths)} missing tracks not found in 04-fix_missing_tracks.csv."
)
