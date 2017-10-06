#!/bin/bash

mkdir -m 777 -p log
rm -rf src
mkdir -m 777 -p src
cd src
git init
git fetch --quiet --depth 1 "https://gerrit.wikimedia.org/r/utfnormal" "refs/changes/57/375857/1"
git checkout FETCH_HEAD
cd ..

mkdir -p log
docker run \
    --rm --tty \
    --volume /$(pwd)/log://var/lib/jenkins/log \
    --volume /$(pwd)/src://src \
     wmfreleng/composer-package:latest
