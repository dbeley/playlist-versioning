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
- all the tracks of an artist are grouped and will be added to the same playlists
- mpc query language is quite limited and only support exact matches

## MPD matching

Create a text file (for example `files/00_favorites-tracks.txt`) containing your favorite tracks (one by line, with the format `ARTIST - TRACK`):
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
./mplaylist.sh files/00_favorites-tracks.txt
```

Output:
- `files/01_result-mplaylist.csv`: tracks matched with mpc
- `files/01_result-mplaylist-missing.csv`: tracks not matched with mpc

## Playlist creation

You will need three files:

- `files/02_playlists.csv` (fields: `playlist_id;playlist_name`):
```
1;Rock
2;Pop
```

- `files/03_artists.csv` (fields: `playlist_id;artist_name`):
```
1;ARTIST1
1;ARTIST3
2;ARTIST2
2;ARTIST1
```

Those two files says "ARTIST1 and ARTIST3 songs will be added to the playlist Rock, and ARTIST1 and ARTIST2 songs to the Pop playlist".

Adding artists in multiple playlists is supported, just duplicate the entries with a different playlist id.

- `files/04_fix-missing-tracks.csv`: manually add paths for the missing tracks in `01_result-mplaylist-missing.csv` (fields: `missing_track;path`):
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

**BASEPATH** indicates what the mpd matched tracks will be prefixed with. It's used to complete the paths as mpd uses internal paths and not full paths.

**LOCAL_BASEPATH** indicates the base path to delete after checking the validity of the manually inserted paths in `04_fix-missing-tracks.csv`. The **BASEPATH** will then be used as a prefix.

By setting **BASEPATH** to `/music/` and **LOCAL_BASEPATH** to `/home/user/nfs/Musique/`, the script will delete `/home/user/nfs/Musique/` from the paths found in `04_fix-missing-tracks.csv` and will create playlists using `/music/` as base path.
If you want to use your playlists on the same filesystem configuration, you can set **LOCAL_BASEPATH** and **BASEPATH** to the same value.

Output:
- `files/03_artists_NOT-FOUND.csv`: artists not found in `03_artists.csv`
- `files/04_fix-missing-tracks_NOT-FOUND.csv`: missing tracks not found in `04_fix-missing-tracks.csv`

If those files are empty you're good, otherwise just add entries in `03_artists.csv` or `04_fix-missing-tracks.csv` and restart the script `create_playlists.py`.

Exported playlists will be in the `playlists` folder.

## Import

I personnaly automatically import those playlists into airsonic (airsonic can watch a folder and automatically import playlists from it).

My music folder is mounted under the `/music/` folder in my airsonic container (hence the `/music/` prefix in `create_playlists.py`).
