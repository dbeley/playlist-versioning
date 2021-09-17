from collections import defaultdict
from pathlib import Path
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import configparser

# Init Spotify
config = configparser.ConfigParser()
config.read("config.ini")
spotify_id = config["spotify"]["id"]
secret = config["spotify"]["secret"]

scope = "playlist-modify-public"

# Create new API keys on developers.spotify.com
# Don't forget to set a redirect_uri to "http://localhost:8080" in your API keys settings
client_credentials_manager = SpotifyOAuth(
    client_id=spotify_id,
    client_secret=secret,
    redirect_uri="http://localhost:8080",
    scope=scope,
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# result of mplaylist.sh
with open("files/00-d_beley_favorite_tracks.csv", "r") as f:
    tracks = [x.strip() for x in f.readlines()]

with open("files/02-playlists.csv", "r") as f:
    corr = dict([x.strip().split(";") for x in f.readlines()])

with open("files/03-artists.csv", "r") as f:
    dict_genres = dict(
        [(x.strip().split(";")[1], x.strip().split(";")[0]) for x in f.readlines()]
    )

# delete NOT_FOUND files if exists
Path("files/03-artists_NOT_FOUND.csv").unlink(missing_ok=True)

list_file = []
list_missing_artists = []
for track in tracks:
    artist = track.split(" - ")[0]
    if artist in dict_genres:
        list_file.append({dict_genres[artist]: track})
    else:
        list_missing_artists.append(artist)

if len(list_missing_artists) > 0:
    missing_artists = set(list_missing_artists)
    for missing_artist in missing_artists:
        print(f"{missing_artist} is missing.")
    print(f"{len(missing_artists)} artists missing!")

    with open("files/03-artists_NOT_FOUND.csv", "w") as f:
        f.write("\n".join(missing_artists))
    exit()

d = defaultdict(list)
for i in list_file:
    k, v = list(i.items())[
        0
    ]  # an alternative to the single-iterating inner loop from the previous solution
    d[k].append(v)

condensed_dict = dict(d)
final_dict = dict()
max_playlist_id = max([int(x) for x in corr])
for k, v in condensed_dict.items():
    if k in corr:
        final_dict[f"{k.zfill(len(str(max_playlist_id)))}_{corr[k]}"] = v
    else:
        print(f"Playlist name {k} not in 02-playlists.csv.")

# print(final_dict)
for playlist_name in final_dict.keys():
    print(f"Playlist {playlist_name}")
    user_id = sp.me()["id"]
    sp.user_playlist_create(user_id, playlist_name)
    playlists = sp.user_playlists(user_id)["items"]
    playlist_id = [x["id"] for x in playlists if x["name"] == playlist_name][0]
    buffer = []
    for track in final_dict[playlist_name]:
        artist, title = track.lower().replace("'", " ").split(" - ", 1)
        # print(f'Processing {track}: Artist "{artist}", Track "{title}".')
        result = sp.search(q=f"{artist} {title}", type="track")
        items = result["tracks"]["items"]
        if len(items) > 0:
            # print(
            # f"Adding {items[0]['artists'][0]['name']} - {items[0]['name']} ({items[0]['album']['name']}) to buffer for playlist {playlist_name}."
            # )
            buffer.append(items[0]["id"])
        else:
            print(f"Nothing found for {track}.")
    sp.playlist_add_items(playlist_id, buffer)
