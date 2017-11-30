#!/bin/bash

mkdir -m 2777 -p log src cache

git init src
git -C src fetch --quiet --depth 1 \
    "https://gerrit.wikimedia.org/r/integration/jenkins" \
    "refs/changes/31/316231/4"
git -C src checkout FETCH_HEAD

docker run \
    --rm --tty \
    --volume /$(pwd)/log:/log \
    --volume /$(pwd)/cache:/cache \
    --volume /$(pwd)/src:/src \
    wmfreleng/composer-test:latest
    # docker-registry.wikimedia.org/releng/composer-test:0.1.0

rm -rf src log cache
