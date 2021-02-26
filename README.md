# playlists

## Dependencies

- mpd/mpc
- python/bash
- a list of your favorite tracks
- a list of artists linked to a playlist

Limitations:
- every track of an artist will be added to the same playlist
- for now an artist can't be added to several playlists
- mpc query language is quite limited and only support exact matches

The script assume the library is organized using `ARTIST/ALBUM/TRACK` folder structure.

## MPD matching

Create a file `files/00-favorites.txt` containing:
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
./mplaylist.sh files/00-favorites.txt
```

- `files/01-result_mplaylist.txt`: tracks matched with mpc
- `files/01-result_mplaylist_missing.txt`: tracks not matched with mpc

## Playlist creation

You will need two files:
- `files/02-artists.csv`: file with playlist_id -> artist_name
```
1;ARTIST1
2;ARTIST2
1;ARTIST3
```

- `files/03-correspondances.csv`: file with playlist_id -> playlist_name
```
1;Rock
2;Pop
```

Run the `create_playlists.py` script:
```
python create_playlists.py
```
It will create playlists from the paths in `01-result_mplaylist.txt`

- `files/04-missing_artists.csv`: artists not found in artists.csv

If it's empty you're good, otherwise just add another entry in `02-artists.csv`.

Exported playlists will be in the `files` folder with the `mplaylist` prefix.

You can use `01-result_mplaylist_missing.txt` to manually add the missing tracks in the playlists.

## Missing tracks

You can also create tracklist for the missing tracks with the `create_tracklists_from_missing.py` script:
```
python create_tracklists_from_missing.py
```
It will create tracklist from the tracks in `01-result_mplaylist_missing.txt`.

- `files/04-missing_artists2.csv`: artists not found in artists.csv

Exported tracklists will be in the `files` folder with the `tracklist` prefix.
