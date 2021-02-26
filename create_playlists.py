from collections import defaultdict

with open("genres/genres.csv", "r") as f:
    dict_genres = dict(
        [(x.strip().split(";")[1], x.strip().split(";")[0]) for x in f.readlines()]
    )

with open("genres/all_favorites.m3u8", "r") as f:
    tracks = [x.strip() for x in f.readlines()]

list_file = []
list_missing_artists = []

for track in tracks:
    artist = track.split("/")[2]
    if artist in dict_genres:
        list_file.append({dict_genres[artist]: track})
    else:
        list_missing_artists.append(artist)

d = defaultdict(list)

for i in list_file:
    k, v = list(i.items())[
        0
    ]  # an alternative to the single-iterating inner loop from the previous solution
    d[k].append(v)

if len(list_missing_artists) > 0:
    missing_artists = set(list_missing_artists)
    for missing_artist in missing_artists:
        print(f"{missing_artist} is missing.")
    print(f"{len(list_missing_artists)} artists missing!")

    with open("genres/missing_artists.csv", "w") as f:
        f.write("\n".join(missing_artists))

final_dict = dict(d)

with open("genres/correspondances.csv", "r") as f:
    corr = dict([x.strip().split(";") for x in f.readlines()])

final_dict2 = dict()
for k, v in final_dict.items():
    if k in corr:
        final_dict2[corr[k]] = v
    else:
        print(f"{k} not in corr")
print(final_dict2)

for playlist, tracks in final_dict2.items():
    print(playlist)
    with open(f"genres/{playlist.replace('/', '-')}.m3u8", "w") as f:
        f.write("\n".join(tracks))
