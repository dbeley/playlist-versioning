# jazz standards

Generate playlists of jazz standards, filtered by an artist allowlist.

## Files

- `jazz_standards.txt`: list of jazz standards (one per line)
- `jazz_artists_allowlist.txt`: list of allowed artists (one per line, lowercase)

## Usage

```
export NAVIDROME_USER="your_user"
export NAVIDROME_PASSWORD="your_password"
./navidrome_jazz_standards.py
```

Output: `jazz_standards.m3u`
