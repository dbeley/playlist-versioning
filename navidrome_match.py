#!/usr/bin/env python3
"""
Match favorite tracks against Navidrome's Subsonic API.

Replaces mplaylist.sh by querying Navidrome's Subsonic API to resolve
ARTIST - TITLE pairs to file paths. Writes matched paths to
files/04_result-mplaylist.csv and unmatched to files/05_result-mplaylist-missing.csv.

Output preserves the order of the input file: each favorite-track line is
processed in file order, and its matching paths are appended to the output
in that same order. This means newly added tracks (at the top of the file)
end up at the bottom of their respective playlists after the pipeline's
reverse ordering.

Usage:
    ./navidrome_match.py [favorite_tracks_file]

Environment variables:
    NAVIDROME_URL          default: http://navidrome.docker-era.home
    NAVIDROME_USER         required
    NAVIDROME_PASSWORD     required
    LIBRARY_ROOT           default: /home/david/nfs/WDC14/Musique/
    NAVIDROME_MAX_WORKERS  default: 10
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

NAVIDROME_URL = os.environ.get(
    "NAVIDROME_URL", "http://navidrome.docker-era.home"
)
NAVIDROME_USER = os.environ.get("NAVIDROME_USER", "")
NAVIDROME_PASSWORD = os.environ.get("NAVIDROME_PASSWORD", "")
LIBRARY_ROOT = os.environ.get(
    "LIBRARY_ROOT", "/home/david/nfs/WDC14/Musique/"
)
MAX_WORKERS = int(os.environ.get("NAVIDROME_MAX_WORKERS", "10"))

FOLDER_PATH = "files"
OUTPUT_MATCHED = f"{FOLDER_PATH}/04_result-mplaylist.csv"
OUTPUT_MISSING = f"{FOLDER_PATH}/05_result-mplaylist-missing.csv"
SEARCH_TIMEOUT = 15


def parse_favorite_tracks(filepath: str) -> list[tuple[str, str]]:
    tracks = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if " - " not in line:
                print(f"WARNING: skipping malformed line: {line}")
                continue
            artist, title = line.split(" - ", 1)
            tracks.append((artist.strip(), title.strip()))
    return tracks


def search_track(
    url: str, user: str, password: str, artist: str, title: str
) -> Optional[list[str]]:
    query = f"{artist} {title}"
    params = urllib.parse.urlencode({
        "u": user,
        "p": password,
        "v": "1.16.0",
        "c": "playlist-versioning",
        "f": "json",
        "query": query,
        "songCount": 20,
    })
    request_url = f"{url}/rest/search2?{params}"

    try:
        req = urllib.request.Request(request_url)
        with urllib.request.urlopen(req, timeout=SEARCH_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        response = data.get("subsonic-response", {})
        if response.get("status") == "failed":
            error = response.get("error", {})
            msg = error.get("message", "unknown error")
            print(f"API error for {artist} - {title}: {msg}")
            return None

        songs = response.get("searchResult2", {}).get("song", [])

        artist_lower = artist.lower()
        title_lower = title.lower()

        matched_paths = []
        for song in songs:
            sa = song.get("artist", "").lower()
            st = song.get("title", "").lower()
            if sa == artist_lower and st == title_lower:
                path = song.get("path", "")
                if path:
                    matched_paths.append(path)

        if not matched_paths:
            for song in songs:
                st = song.get("title", "").lower()
                if st == title_lower:
                    path = song.get("path", "")
                    if path and path not in matched_paths:
                        matched_paths.append(path)

        return matched_paths if matched_paths else None

    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("ERROR: Authentication failed. Check NAVIDROME_USER and NAVIDROME_PASSWORD.")
            sys.exit(1)
        print(f"HTTP error {e.code} for {artist} - {title}: {e.reason}")
        return None
    except urllib.error.URLError as e:
        reason = e.reason if isinstance(e.reason, str) else str(e.reason)
        print(f"Connection error for {artist} - {title}: {reason}")
        return None
    except json.JSONDecodeError:
        print(f"Invalid JSON response for {artist} - {title}")
        return None


def strip_library_root(path: str) -> str:
    if path.startswith(LIBRARY_ROOT):
        return path[len(LIBRARY_ROOT):]
    return path


def main():
    if len(sys.argv) > 1:
        favorite_file = sys.argv[1]
    else:
        favorite_file = f"{FOLDER_PATH}/00_dbeley-favorite-tracks.txt"

    if not NAVIDROME_USER or not NAVIDROME_PASSWORD:
        print("ERROR: NAVIDROME_USER and NAVIDROME_PASSWORD must be set.")
        sys.exit(1)

    print(f"Reading favorite tracks from {favorite_file}")
    tracks = parse_favorite_tracks(favorite_file)
    if not tracks:
        print("No tracks to match. Exiting.")
        return
    print(f"Found {len(tracks)} tracks to match")

    # Store results keyed by original file-line index
    results_by_index: dict[int, list[str]] = {}
    missing_by_index: dict[int, str] = {}

    def process_track(
        idx: int, artist: str, title: str
    ) -> tuple[int, Optional[list[str]], Optional[str]]:
        result = search_track(
            NAVIDROME_URL, NAVIDROME_USER, NAVIDROME_PASSWORD, artist, title
        )
        if result:
            paths = [strip_library_root(p) for p in result]
            return (idx, paths, None)
        else:
            return (idx, None, f"{artist} - {title}")

    print(f"Matching tracks against Navidrome ({NAVIDROME_URL})...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(process_track, i, a, t): i
            for i, (a, t) in enumerate(tracks)
        }
        done = 0
        for future in as_completed(futures):
            done += 1
            if done % 100 == 0 or done == len(tracks) or done == 1:
                print(f"  Progress: {done}/{len(tracks)}")

            idx, paths, missing_str = future.result()
            if paths:
                results_by_index[idx] = paths
            else:
                missing_by_index[idx] = missing_str

    # Reconstruct output in file order
    seen_paths: set[str] = set()
    ordered_matched: list[str] = []
    ordered_missing: list[str] = []

    for idx in range(len(tracks)):
        if idx in results_by_index:
            for path in results_by_index[idx]:
                if path not in seen_paths:
                    seen_paths.add(path)
                    ordered_matched.append(path)
        if idx in missing_by_index:
            ordered_missing.append(missing_by_index[idx])

    Path(OUTPUT_MATCHED).unlink(missing_ok=True)
    Path(OUTPUT_MISSING).unlink(missing_ok=True)

    with open(OUTPUT_MATCHED, "w", encoding="utf-8") as f:
        f.write("\n".join(ordered_matched))
        if ordered_matched:
            f.write("\n")

    with open(OUTPUT_MISSING, "w", encoding="utf-8") as f:
        f.write("\n".join(ordered_missing))
        if ordered_missing:
            f.write("\n")

    print(
        f"\nDone! {len(ordered_matched)} tracks matched, "
        f"{len(ordered_missing)} missing."
    )
    print(f"  Matched: {OUTPUT_MATCHED}")
    print(f"  Missing: {OUTPUT_MISSING}")


if __name__ == "__main__":
    main()
