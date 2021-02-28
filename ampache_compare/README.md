```
python ampache_compare.py
vim sort u
```

Comparison between old ampache playlists with current ones.

```
diff -i -u 00-ampache_favorite_tracks.csv 00-current_favorite_tracks.csv | grep -E "^\-" > missing_in_current.csv
```
