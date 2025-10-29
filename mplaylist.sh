#!/usr/bin/env bash
set -eEu -o pipefail
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd -P)"

usage() { printf "%s" "\
Usage:      ./mplaylist.sh [-h] FILE
"; exit 0;
}

if [ "$1" == "-h" ]; then
    usage
fi

FILE=$1
OUTPUT_FILE="$DIR/files/04_result-mplaylist.csv"
OUTPUT_FILE_MISSING="$DIR/files/05_result-mplaylist-missing.csv"

if [ -f $OUTPUT_FILE ]; then
   printf "File $OUTPUT_FILE exists. Deleting.\n"
   rm $OUTPUT_FILE
fi

if [ -f $OUTPUT_FILE_MISSING ]; then
   printf "File $OUTPUT_FILE_MISSING exists. Deleting.\n"
   rm $OUTPUT_FILE_MISSING
fi

printf "Processing tracks from $FILE.\n"

# Process file without modifying the original
while read -r name; do
	# Remove quotes and parse artist/track in one awk call
	read -r artist track < <(awk -F " - " '{gsub(/"/, "", $1); gsub(/"/, "", $2); print $1; print $2}' <<<"$name")
	
	# Trim whitespace efficiently
	artist="${artist#"${artist%%[![:space:]]*}"}"
	artist="${artist%"${artist##*[![:space:]]}"}"
	track="${track#"${track%%[![:space:]]*}"}"
	track="${track%"${track##*[![:space:]]}"}"

	# Skip empty lines
	[ -z "$artist" ] && continue
	
	# printf "mpc search ((artist == \"$artist\") AND (title == \"$track\"))\n"
	potential_tracks=$(mpc search "((artist == \"$artist\") AND (title == \"$track\"))")
	if [[ $potential_tracks ]]; then
		printf "$potential_tracks\n" >> $OUTPUT_FILE
	else
		printf "Track $artist - $track not found in mpd database.\n"
		printf "$artist - $track\n" >> $OUTPUT_FILE_MISSING
	fi
done < "$FILE"
