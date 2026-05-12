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
    total = len(standards)

    for idx, title in enumerate(standards, 1):
        songs = search_title(title)
        title_lower = title.lower()

        found = False
        for song in songs:
            st = song.get("title", "").lower()
            if st != title_lower:
                alt_title = title.replace("'", "’").lower()
                if st != alt_title:
                    continue

            artist_name = song.get("artist", "").lower()
            path = song.get("path", "")

            for allowed in allowlist:
                if artist_name.startswith(allowed):
                    if path.startswith(LIBRARY_ROOT):
                        path = f"/music/{path[len(LIBRARY_ROOT):]}"
                    else:
                        path = f"/music/{path}"

                    if path not in matched_tracks:
                        matched_tracks.append(path)
                    found = True
                    break

        if not found and (idx <= 3 or idx == total):
            print(f"No match for: {title}")

        if idx % 50 == 0:
            print(f"  Progress: {idx}/{total}")

    matched_tracks.sort()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(matched_tracks))
        if matched_tracks:
            f.write("\n")

    # Remove old MPD-specific output
    mpd_file = SCRIPT_DIR / "jazz_standards_mpd.m3u"
    mpd_file.unlink(missing_ok=True)

    print(f"\nDone! {len(matched_tracks)} tracks written to {OUTPUT_FILE.name}")


if __name__ == "__main__":
    main()
