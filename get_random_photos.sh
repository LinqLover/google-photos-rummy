#!/usr/bin/env bash
if [ "$#" -ne 2 ]; then
	echo "usage: get_random_files.sh <directory> <number of files>"
	exit 1
fi

find "$1" -type f -name "*.jpeg" -o -name "*.jpg" | shuf -n "$2" | xargs -I {} cp {} .
