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

while read name; do
	artist="$(awk -F " - " '{printf $1}' <<<$name)"
	track="$(awk -F " - " '{printf $2}' <<<$name)"

    artist="${artist#"${artist%%[![:space:]]*}"}"
    # remove trailing whitespace characters
    artist="${artist%"${artist##*[![:space:]]}"}"

    # remove leading whitespace characters
    track="${track#"${track%%[![:space:]]*}"}"
    # remove trailing whitespace characters
    track="${track%"${track##*[![:space:]]}"}"

	potential_tracks=$(mpc search "((artist == \"$artist\") AND (title == \"$track\"))" )
	if [[ $potential_tracks ]]; then
    	printf "$potential_tracks" >> files/01-result_mplaylist.txt
	else
		printf "No track found for = $artist - $track\n"
		printf "$artist - $track\n" >> files/01-result_mplaylist_missing.txt
	fi

done < "$FILE"
