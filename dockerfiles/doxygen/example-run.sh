#!/bin/bash

set -eux -o pipefail

mkdir -m 777 -p log
mkdir -m 777 -p src
mkdir -m 777 -p cache

(cd src
 git init
 git fetch --quiet --depth 1 "https://gerrit.wikimedia.org/r/mediawiki/oauthclient-php"
 git checkout FETCH_HEAD
)

echo "Cleaning generated documentation in /src/doc"
docker run \
    --rm --tty \
    --volume /"$(pwd)"/src://src \
    --entrypoint=/bin/rm \
    docker-registry.wikimedia.org/releng/doxygen:latest \
    -fR /src/doc

docker run \
    --rm --tty \
    --volume /"$(pwd)"/log://var/lib/jenkins/log \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/src://src \
    docker-registry.wikimedia.org/releng/doxygen:latest

set +x
if [ -e src/doc/html/index.html ]; then
    echo "Doxygen documentation generated"
else
    echo "Doxygen documentation has NOT been generated"
    exit 1
fi
