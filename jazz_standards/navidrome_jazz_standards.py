#!/usr/bin/env python3
"""
Build jazz standards playlists from Navidrome's Subsonic API.

Replaces mplaylist_jazz_standards.sh by searching Navidrome by
title, then filtering results against an artist allowlist.

Usage:
    ./navidrome_jazz_standards.py

Environment variables:
    NAVIDROME_URL          default: http://navidrome.docker-era.home
    NAVIDROME_USER         required
    NAVIDROME_PASSWORD     required
    LIBRARY_ROOT           default: /home/david/nfs/WDC14/Musique/
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

NAVIDROME_URL = os.environ.get(
    "NAVIDROME_URL", "http://navidrome.docker-era.home"
)
NAVIDROME_USER = os.environ.get("NAVIDROME_USER", "")
NAVIDROME_PASSWORD = os.environ.get("NAVIDROME_PASSWORD", "")
LIBRARY_ROOT = os.environ.get(
    "LIBRARY_ROOT", "/home/david/nfs/WDC14/Musique/"
)

SCRIPT_DIR = Path(__file__).parent
STANDARDS_FILE = SCRIPT_DIR / "jazz_standards.txt"
ALLOWLIST_FILE = SCRIPT_DIR / "jazz_artists_allowlist.txt"
OUTPUT_FILE = SCRIPT_DIR / "jazz_standards.m3u"

SEARCH_TIMEOUT = 15

# Common punctuation substitutions for matching
_PUNCT_TABLE = str.maketrans({
    "’": "'",
    "ʼ": "'",
    "‘": "'",
    "′": "'",
    "`": "'",
    "\"": "",
    '"': "",
    " ": " ",  # narrow no-break space
    "\u2013": "-",
    "\u2014": "-",
})


def normalize(s: str) -> str:
    return s.lower().strip().translate(_PUNCT_TABLE)


def titles_match(standard: str, song_title: str) -> bool:
    a = normalize(standard)
    b = normalize(song_title)
    return a == b or a in b or b in a


def load_allowlist() -> list[str]:
    artists = []
    with open(ALLOWLIST_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                artists.append(line.lower())
    return artists


def load_standards() -> list[str]:
    titles = []
    with open(STANDARDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                titles.append(line)
    return titles


def search_title(title: str) -> list[dict]:
    params = urllib.parse.urlencode({
        "u": NAVIDROME_USER,
        "p": NAVIDROME_PASSWORD,
        "v": "1.16.0",
        "c": "jazz-standards",
        "f": "json",
        "query": title,
        "songCount": 100,
    })
    url = f"{NAVIDROME_URL}/rest/search2?{params}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=SEARCH_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        response = data.get("subsonic-response", {})
        if response.get("status") == "failed":
            error = response.get("error", {})
            print(f"API error: {error.get('message', 'unknown error')}")
            return []

        return response.get("searchResult2", {}).get("song", [])

    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("ERROR: Authentication failed.")
            sys.exit(1)
        print(f"HTTP error {e.code}: {e.reason}")
        return []
    except urllib.error.URLError as e:
        reason = e.reason if isinstance(e.reason, str) else str(e.reason)
        print(f"Connection error: {reason}")
        return []
    except json.JSONDecodeError:
        print(f"Invalid JSON response for title: {title}")
        return []


def main():
    if not NAVIDROME_USER or not NAVIDROME_PASSWORD:
        print("ERROR: NAVIDROME_USER and NAVIDROME_PASSWORD must be set.")
        sys.exit(1)

    allowlist = load_allowlist()
    standards = load_standards()
    print(f"Loaded {len(allowlist)} allowed artists, {len(standards)} standards")

    matched_tracks: list[str] = []
    candidates: dict[str, set[str]] = {}  # artist -> set of matched titles
    unknown_titles: list[str] = []
    total = len(standards)

    def is_allowed(artist_lower: str) -> bool:
        for allowed in allowlist:
            if artist_lower.startswith(allowed):
                return True
        return False

    for idx, title in enumerate(standards, 1):
        songs = search_title(title)

        title_matched = False
        for song in songs:
            st = song.get("title", "")
            if not titles_match(title, st):
                continue

            title_matched = True
            artist_name = song.get("artist", "")
            artist_lower = artist_name.lower()
            path = song.get("path", "")

            if is_allowed(artist_lower):
                if path.startswith(LIBRARY_ROOT):
                    path = f"/music/{path[len(LIBRARY_ROOT):]}"
                else:
                    path = f"/music/{path}"

                if path not in matched_tracks:
                    matched_tracks.append(path)
            else:
                if artist_lower not in candidates:
                    candidates[artist_lower] = set()
                candidates[artist_lower].add(title)

        if not title_matched:
            unknown_titles.append(title)

        if idx % 50 == 0 or idx == total or idx == 1:
            print(f"  Progress: {idx}/{total}")

    matched_tracks.sort()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(matched_tracks))
        if matched_tracks:
            f.write("\n")

    mpd_file = SCRIPT_DIR / "jazz_standards_mpd.m3u"
    mpd_file.unlink(missing_ok=True)

    print(f"\nDone! {len(matched_tracks)} tracks written to {OUTPUT_FILE.name}")

    if candidates:
        print(
            f"\n{len(candidates)} candidate artists found (not in allowlist)."
        )
        print("Consider adding these to jazz_artists_allowlist.txt:")
        print()
        for artist in sorted(candidates):
            titles = sorted(candidates[artist])
            print(f"  {artist}  ({len(titles)} standards: {', '.join(titles[:5])}"
                  f"{', ...' if len(titles) > 5 else ''})")
        print()

    if unknown_titles:
        print(f"\n{len(unknown_titles)} standards with no match in library:")
        for t in unknown_titles:
            print(f"  - {t}")
        print()


if __name__ == "__main__":
    main()
