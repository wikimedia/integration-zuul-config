#!/bin/bash

set -eux -o pipefail

mkdir -m 777 -p log
mkdir -m 777 -p src
mkdir -m 777 -p cache

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
    -e ZUUL_URL=https://gerrit.wikimedia.org/r/ \
    -e ZUUL_PROJECT=oojs/ui \
    -e ZUUL_REF=master \
    docker-registry.wikimedia.org/releng/doxygen:latest

set +x
if [ -e src/doc/html/index.html ]; then
    echo "Doxygen documentation generated"
else
    echo "Doxygen documentation has NOT been generated"
    exit 1
fi
