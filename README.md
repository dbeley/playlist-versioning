# playlists

## Dependencies

- mpd with a library
- mpc
- python
- bash

## MPD matching

Create a file `files/00-favorites.txt` containing:
```
ARTIST1 - FAVORITE_TRACK1
ARTIST1 - FAVORITE_TRACK2
ARTIST2 - FAVORITE_TRACK3
ARTIST3 - FAVORITE_TRACK4
...
```

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

- `files/04-missing_artists.csv`: artists not found in artists.csv

If it's empty you're good, otherwise just add another entry in `02-artists.csv`.

Exported playlists will be in the `files` folder.

You can use `01-result_mplaylist_missing.txt` to manually add the missing tracks in the playlists.
