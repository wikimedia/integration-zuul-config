#!/bin/bash

set -euo pipefail

mkdir -m 777 -p cache log src
(
cd src
git init
git fetch --quiet --depth 1 "https://gerrit.wikimedia.org/r/mediawiki/skins/MinervaNeue" "refs/changes/01/387501/1"
git checkout FETCH_HEAD
)

docker run \
    --rm --tty \
    --volume /"$(pwd)"/log://var/lib/jenkins/log \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/src://src \
    docker-registry.wikimedia.org/releng/node10:latest
