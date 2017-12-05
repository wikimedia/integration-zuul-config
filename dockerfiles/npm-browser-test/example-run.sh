#!/bin/bash

set -euo pipefail

mkdir -m 777 -p log
mkdir -m 777 -p src
mkdir -m 777 -p cache
mkdir -m 777 -p cache/node_modules
cd src
git init
git fetch --quiet --depth 1 https://gerrit.wikimedia.org/r/VisualEditor/VisualEditor
git checkout FETCH_HEAD
cd ..

docker run \
    --rm --tty \
    --volume /"$(pwd)"/log://var/lib/jenkins/log \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/cache/node_modules://src/node_modules \
    --volume /"$(pwd)"/log://log \
    --volume /"$(pwd)"/src://src \
     wmfreleng/npm-browser-test:latest
rm -rf log
