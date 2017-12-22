#!/bin/bash

set -eux -o pipefail

mkdir -m 777 -p log
mkdir -m 777 -p src
mkdir -m 777 -p cache

(cd src
 git init
 git fetch --quiet --depth 1 "https://gerrit.wikimedia.org/r/mediawiki/skins/MinervaNeue" "master"
 git checkout FETCH_HEAD
)

# NPM_RUN_SCRIPT=doc => npm run-script doc
docker run \
    --rm --tty \
    -e NPM_RUN_SCRIPT=doc \
    --volume /"$(pwd)"/log://var/lib/jenkins/log \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/src://src \
     wmfreleng/npm-test:latest

if grep -q JSDuck src/docs/index.html; then
    echo "JSDuck documentation has been generated"
else
    echo "'npm run-script doc' failed to generate docs/index.html"
    exit 1
fi

docker run \
    --rm --tty \
    --volume /"$(pwd)"/log://var/lib/jenkins/log \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/src://src \
     wmfreleng/npm-test:latest
