#!/bin/bash

set -eux -o pipefail

mkdir -m 2777 -p log
mkdir -m 2777 -p src
mkdir -m 2777 -p cache

docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=oojs/ui \
    --env ZUUL_COMMIT=master \
    --env ZUUL_REF=master \
    --volume "/$(pwd)/src://src" \
        docker-registry.wikimedia.org/releng/ci-src-setup-simple:latest

docker run \
    --rm --tty \
    --volume /"$(pwd)"/log://var/lib/jenkins/log \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/src://src \
    docker-registry.wikimedia.org/releng/npm-test-oojsui:latest
