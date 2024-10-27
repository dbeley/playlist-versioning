#!/usr/bin/env bash
set -eEu -o pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd -P)"

usage() { printf "%s" "\
Usage:      ./mplaylist_jazz_standards.sh [-h]
"; exit 0;
}

JAZZ_STANDARDS_FILE="$DIR/jazz_standards.txt"
JAZZ_ARTISTS_ALLOWLIST_FILE="$DIR/jazz_artists_allowlist.txt"
OUTPUT_FILE="$DIR/jazz_standards.m3u"

if [ -f $OUTPUT_FILE ]; then
   printf "File $OUTPUT_FILE exists. Deleting.\n"
   rm $OUTPUT_FILE
fi

while read name; do

  # Replace ' with ’ in name and store both original and modified versions
  alt_name="${name//\'/’}"
  # Search for potential tracks with both versions of the title
  potential_tracks=$( { mpc search title "$name"; mpc search title "$alt_name"; } | sort -u)

	if [[ $potential_tracks ]]; then
    while read -r track_path; do
      # Extract the part before the first slash
      artist_name=$(echo "$track_path" | cut -d'/' -f1)

      match_found=false
      while read -r allowed_artist; do
          if [[ "${artist_name,,}" == "${allowed_artist,,}"* ]]; then
              match_found=true
              break
          fi
      done < "$JAZZ_ARTISTS_ALLOWLIST_FILE"

      # If match is found, append the track to the output file
      if $match_found; then
          printf "%s\n" "$track_path" >> "$OUTPUT_FILE"
      else
          printf "Artist $artist_name not found in allowlist.\n"
      fi
  done <<< "$potential_tracks"
	fi
done < "$JAZZ_STANDARDS_FILE"
