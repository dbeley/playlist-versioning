#!/usr/bin/env bash
set -eEu -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

usage() {
  echo "Usage: $0 [-h]"
  exit 0
}

JAZZ_STANDARDS_FILE="$DIR/jazz_standards.txt"
JAZZ_ARTISTS_ALLOWLIST_FILE="$DIR/jazz_artists_allowlist.txt"
OUTPUT_FILE="$DIR/jazz_standards.m3u"
OUTPUT_FILE_MPD="$DIR/jazz_standards_mpd.m3u"

# Check if required files exist
[[ -f "$JAZZ_STANDARDS_FILE" ]] || {
  echo "Error: jazz_standards.txt file not found."
  exit 1
}
[[ -f "$JAZZ_ARTISTS_ALLOWLIST_FILE" ]] || {
  echo "Error: jazz_artists_allowlist.txt file not found."
  exit 1
}

# Remove output files if they exist
for file in "$OUTPUT_FILE" "$OUTPUT_FILE_MPD"; do
  if [[ -f "$file" ]]; then
    echo "File $file exists. Deleting."
    rm "$file"
  fi
done

# Load allowed artists into an array for prefix matching
allowed_artists=()
while read -r allowed_artist; do
  [[ "$allowed_artist" =~ ^# ]] && continue # Skip comments
  allowed_artists+=("${allowed_artist,,}")  # Convert to lowercase for case-insensitive matching
done <"$JAZZ_ARTISTS_ALLOWLIST_FILE"

# Read and process each jazz standard name
while read -r name; do
  [[ "$name" =~ ^# ]] && continue # Skip comments

  alt_name="${name//\'/’}"
  # potential_tracks=$( { mpc search "(title == \"$name\")"; mpc search "(title == \"$alt_name\")"; } | sort -u)
  potential_tracks=$({
    mpc search title "$name"
    mpc search title "$alt_name"
  } | sort -u)

  if [[ -n "$potential_tracks" ]]; then
    while read -r track_path; do
      artist_name=$(echo "$track_path" | cut -d'/' -f1 | tr '[:upper:]' '[:lower:]')

      # Check if artist_name starts with any allowed artist prefix
      match_found=false
      for allowed_artist in "${allowed_artists[@]}"; do
        if [[ "$artist_name" == "$allowed_artist"* ]]; then
          match_found=true
          break
        fi
      done

      # If match is found, append the track to the output file
      if $match_found; then
        echo "/music/$track_path" >>"$OUTPUT_FILE"
        echo "$track_path" >>"$OUTPUT_FILE_MPD"
      else
        echo "Artist $artist_name not found in allowlist (current track name $name)."
      fi
    done <<<"$potential_tracks"
  fi
done <"$JAZZ_STANDARDS_FILE"
