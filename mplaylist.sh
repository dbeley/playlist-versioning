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

if [ -f "$OUTPUT_FILE" ]; then
   printf 'File %s exists. Deleting.\n' "$OUTPUT_FILE"
   rm "$OUTPUT_FILE"
fi

if [ -f "$OUTPUT_FILE_MISSING" ]; then
   printf 'File %s exists. Deleting.\n' "$OUTPUT_FILE_MISSING"
   rm "$OUTPUT_FILE_MISSING"
fi

printf 'Replacing double quotes in file %s.\n' "$FILE"
sed -i 's/"//g' "$FILE"

while read -r name; do
        artist="$(awk -F " - " '{printf $1}' <<<"$name")"
        track="$(awk -F " - " '{printf $2}' <<<"$name")"

	# remove leading whitespace characters
	artist="${artist#"${artist%%[![:space:]]*}"}"
	# remove trailing whitespace characters
	artist="${artist%"${artist##*[![:space:]]}"}"

	# remove leading whitespace characters
	track="${track#"${track%%[![:space:]]*}"}"
	# remove trailing whitespace characters
	track="${track%"${track##*[![:space:]]}"}"

	# printf "mpc search ((artist == \"$artist\") AND (title == \"$track\"))\n"
        potential_tracks=$(mpc search "((artist == \"$artist\") AND (title == \"$track\"))")
        if [[ $potential_tracks ]]; then
                printf '%s\n' "$potential_tracks" >> "$OUTPUT_FILE"
        else
                printf 'Track %s - %s not found in mpd database.\n' "$artist" "$track"
                printf '%s - %s\n' "$artist" "$track" >> "$OUTPUT_FILE_MISSING"
        fi
done < "$FILE"
#done < "$FILE" | head -n 15
