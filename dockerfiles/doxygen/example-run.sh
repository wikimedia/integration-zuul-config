#!/bin/bash

mkdir -m 777 -p src
cd src
git init
git fetch --quiet --depth 1 "https://gerrit.wikimedia.org/r/utfnormal" "refs/changes/57/375857/1"
git checkout FETCH_HEAD
cd ..

docker run \
    --rm --tty \
    --volume /$(pwd)/src://src \
     wmfreleng/doxygen:latest
rm -rf src
