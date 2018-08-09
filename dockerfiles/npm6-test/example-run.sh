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

# Arguments are passed to 'npm run-script',eg 'doc'
docker run \
    --rm --tty \
    --volume /"$(pwd)"/log://var/lib/jenkins/log \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/src://src \
    docker-registry.wikimedia.org/releng/npm-test:latest \
        doc

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
    docker-registry.wikimedia.org/releng/npm-test:latest
