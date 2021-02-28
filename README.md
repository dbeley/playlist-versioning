# playlists

My playlists under version control.

## Requirements

- mpd/mpc
- python/bash
- a list of your favorite tracks
- a list of artists linked to a playlist

Limitations:
- every track of an artist will be added to the same playlist
- for now an artist can't be added to several playlists
- mpc query language is quite limited and only support exact matches

The script assume the library is organized with `ARTIST/ALBUM/TRACK` as folder structure.

## MPD matching

Create a file `files/00-favorites.csv` containing your favorite tracks:
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
./mplaylist.sh files/00-favorites.csv
```

If you run `mplaylist.sh` after another run, don't forget to delete the previous output as the script append their results to the output files.

Output:
- `files/01-result_mplaylist.csv`: tracks matched with mpc
- `files/01-result_mplaylist_missing.csv`: tracks not matched with mpc

## Playlist creation

You will need three files:
- `files/03-artists.csv` (file with fields `playlist_id;artist_name`):
```
1;ARTIST1
2;ARTIST2
1;ARTIST3
```

- `files/02-playlists.csv` (file with fields `playlist_id;playlist_name`):
```
1;Rock
2;Pop
```

- `files/04-missing_tracks.csv`: used to manually add paths for the missing tracks in `01-result_mplaylist_missing.csv` (file with fields `artist-missing_track;path`):
```
ARTIST1 - MISSING_TRACK1;PATH_TO_TRACK1
ARTIST2 - MISSING_TRACK2;PATH_TO_TRACK2
ARTIST2 - MISSING_TRACK3;PATH_TO_TRACK3
ARTIST3 - MISSING_TRACK4;PATH_TO_TRACK4
```

Run the `create_playlists.py` script (change the *LOCAL_BASEPATH* and *BASEPATH* global variable to your own):
```
python create_playlists.py
```

The script will try to match the missing tracks in `01-result_mplaylist_missing.csv` with `04-tracklist_matching.csv`. Unmatched tracks will be written in `04-missing_tracks_missing.csv`.

- `files/03-missing_artists.csv`: artists not found in `03-artists.csv`
- `files/04-missing_tracks_missing.csv`: missing tracks not found in `04-missing_tracks.csv`

If those files are empty you're good, otherwise just add entries in `03-artists.csv` or `04-missing_tracks.csv`.

Exported playlists will be in the `files` folder with the `mplaylist` prefix.

## Import

I personnaly import those playlists into airsonic.

My music folder is mounted under the `/music/` folder in my airsonic container (hence the `/music/` prefix in `create_playlists.py`).

## Troubleshooting

### `MPD Error: ')' expected

Most likely due to a malformed input file. If there are quotes in your input file `"`, you will have to escape them `\"`.

### Folders

- files : output files
- ampache_backup : my old ampache backup
- diff : parsed ampache backup, to be compared with files in `files`
