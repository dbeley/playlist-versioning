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
	artist="$(cut -d'-' -f1 <<<$name)"
	track="$(cut -d'-' -f2 <<<$name)"

    artist="${artist#"${artist%%[![:space:]]*}"}"
    # remove trailing whitespace characters
    artist="${artist%"${artist##*[![:space:]]}"}"

    # remove leading whitespace characters
    track="${track#"${track%%[![:space:]]*}"}"
    # remove trailing whitespace characters
    track="${track%"${track##*[![:space:]]}"}"
	printf "mpc search '((artist == \"$artist\") AND (title == \"$track\"))'\n"
	mpc search "((artist == \"$artist\") AND (title == \"$track\"))"
	# result=$(mpc search "((artist == \"$artist\") AND (title == \"$track\"))")
	mpc search "((artist == \"$artist\") AND (title == \"$track\"))" >> playlist2.txt

done < "$FILE"
