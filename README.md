# playlists

My playlists under version control.

## Requirements

- mpd (with your library imported)
- mpc
- python
- bash
- a list of your favorite tracks
- a list of artists linked to a playlist (see below)

Limitations:
- every track of an artist will be added to the same playlist
- for now an artist can't be added to several playlists
- mpc query language is quite limited and only support exact matches

## MPD matching

Create a file `files/00-favorites_tracks.csv` containing your favorite tracks:
```
ARTIST1 - FAVORITE_TRACK1
ARTIST1 - FAVORITE_TRACK2
ARTIST2 - FAVORITE_TRACK3
ARTIST3 - FAVORITE_TRACK4
...
```

I personnaly export all my favorite tracks on last.fm with [this script](https://github.com/dbeley/lastfm-scraper/blob/master/lastfm-all_favorite_tracks.py).

Run the `mplaylist.sh` script:
```
./mplaylist.sh files/00-favorites_tracks.csv
```

Output:
- `files/01-result_mplaylist.csv`: tracks matched with mpc
- `files/01-result_mplaylist_missing.csv`: tracks not matched with mpc

## Playlist creation

You will need three files:

- `files/02-playlists.csv` (fields: `playlist_id;playlist_name`):
```
1;Rock
2;Pop
```

- `files/03-artists.csv` (fields: `playlist_id;artist_name`):
```
1;ARTIST1
2;ARTIST2
1;ARTIST3
```

Those two files says "ARTIST1 and ARTIST3 songs will be added to the playlist Rock, and ARTIST2 songs to the Pop playlist".

- `files/04-fix_missing_tracks.csv`: manually add paths for the missing tracks in `01-result_mplaylist_missing.csl` (fields: `missing_track;path`):
```
ARTIST1 - MISSING_TRACK1;PATH_TO_TRACK1
ARTIST2 - MISSING_TRACK2;PATH_TO_TRACK2
ARTIST2 - MISSING_TRACK3;PATH_TO_TRACK3
ARTIST3 - MISSING_TRACK4;PATH_TO_TRACK4
```

Run the `create_playlists.py` script (change the **LOCAL_BASEPATH** and **BASEPATH** global variable to your own):
```
python create_playlists.py
```

**LOCAL_BASEPATH** indicates what part of the paths will be replaced by **BASEPATH**. It's useful to create playlists to be imported into a container (you might want your `~/nfs/Musique` local folder to become `/music`). You can set both variables to the same value if you don't want the paths to be modified.

Output:
- `files/03-artists_NOT_FOUND.csv`: artists not found in `03-artists.csv`
- `files/04-fix_missing_tracks_NOT_FOUND.csv`: missing tracks not found in `04-fix_missing_tracks.csv`

If those files are empty you're good, otherwise just add entries in `03-artists.csv` or `04-fix_missing_tracks.csv` and restart the script `create_playlists.py`.

Exported playlists will be in the `playlists` folder.

## Import

I personnaly import those playlists into airsonic.

My music folder is mounted under the `/music/` folder in my airsonic container (hence the `/music/` prefix in `create_playlists.py`).
