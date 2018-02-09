#!/bin/bash

set -eux -o pipefail

install --mode 777 --directory cache src

echo "Cloning mediawiki/core"
docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=mediawiki/core \
    --env ZUUL_COMMIT=master \
    --env ZUUL_REF=master \
    --volume "/$(pwd)/cache://cache" \
    --volume "/$(pwd)/src://src" \
    docker-registry.wikimedia.org/releng/ci-src-setup-simple:latest

echo "Cleaning generated documentation in /src/docs/js"
docker run \
    --rm --tty \
    --volume /"$(pwd)"/src://src \
    --entrypoint=/bin/rm \
    docker-registry.wikimedia.org/releng/jsduck:latest \
    -fR /src/docs/js

echo "Running JSDuck"
docker run \
    --rm --tty \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/src://src \
    docker-registry.wikimedia.org/releng/jsduck:latest

if grep -q JSDuck src/docs/js/index.html; then
    echo "JSDuck documentation has been generated"
else
    echo "JSDuck Failed to generate docs/index.html"
    exit 1
fi
