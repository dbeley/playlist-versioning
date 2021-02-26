# playlists

Tool to create playlists for mpd from a text file

`files/00-INPUT.txt`:
```
ARTIST1 - FAVORITE_TRACK1
ARTIST1 - FAVORITE_TRACK2
ARTIST2 - FAVORITE_TRACK3
ARTIST3 - FAVORITE_TRACK4
...
```

```
./mplaylist.sh files/00-INPUT.txt
```

- files/01-result_mplaylist.txt : tracks matched in mpc
- files/01-result_mplaylist_missing.txt : tracks not matched in mpc

- files/02-artists.csv: file with playlist_id -> artist_name
```
1;ARTIST1
2;ARTIST2
1;ARTIST3
```

- files/03-correspondances.csv:  file with playlist_id -> playlist_name
```
1;Rock
2;Pop
```

```
python create_playlists.py
```

- files/04-missing_artists.csv: artists not found in artists.csv
