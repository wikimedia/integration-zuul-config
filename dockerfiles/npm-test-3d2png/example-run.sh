#!/bin/bash

set -eux -o pipefail

mkdir -m 777 -p log
mkdir -m 777 -p src
mkdir -m 777 -p cache

(
cd src
git init
git fetch --quiet --depth 1 "https://gerrit.wikimedia.org/r/3d2png"
git checkout FETCH_HEAD
)

docker run \
    --rm --tty \
    --volume /"$(pwd)"/log://var/lib/jenkins/log \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/src://src \
    docker-registry.wikimedia.org/releng/npm-test-3d2png:latest
