#!/bin/bash

set -euo pipefail

mkdir -m 777 -p cache log src
(
cd src
git init
git fetch --quiet --depth 1 https://gerrit.wikimedia.org/r/data-values/value-view
git checkout FETCH_HEAD
)

docker run \
    --rm --tty \
    --volume /"$(pwd)"/log://var/lib/jenkins/log \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/log://log \
    --volume /"$(pwd)"/src://src \
    docker-registry.wikimedia.org/releng/node10-test-browser:latest
