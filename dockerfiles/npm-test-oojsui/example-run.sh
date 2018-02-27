#!/bin/bash

set -eux -o pipefail

mkdir -m 2777 -p log
mkdir -m 2777 -p src
mkdir -m 2777 -p cache

#(
#cd src
#git init
#git fetch --quiet --depth 1 "https://gerrit.wikimedia.org/r/oojs/ui"
#git checkout FETCH_HEAD
#)

docker run \
    --rm --tty \
    --volume /"$(pwd)"/log://var/lib/jenkins/log \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/src://src \
    docker-registry.wikimedia.org/releng/npm-test-oojsui:latest
