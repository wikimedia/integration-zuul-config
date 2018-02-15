#!/bin/bash

set -euo pipefail

function usage() {
    echo "Usage: $0 <directory> [options]"
    echo ""
    echo "<directory>   path to a directory holding composer.json"
    echo "[options]     extra options passed to 'composer require'"
    echo "              ex: --profile --ignore-platform-reqs"
    exit 1
}

[ -z "${1:-}" ] && usage

if [ ! -d "$1" ] && [ ! -f "$1"/composer.json ]; then
    echo "$1 must be a directory and hold composer.json"
    usage
fi

basedir=$1

shift
options=(${@})
set -x

(cd "$basedir"
 jq -r '.["require-dev"]|to_entries|map([.key,.value])[]|join("=")' composer.json \
     | xargs --verbose composer require --dev --ansi --no-progress --prefer-dist -v "${options[@]}"
)
