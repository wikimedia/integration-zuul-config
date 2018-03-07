#!/bin/bash

set -euxo pipefail

install --mode 2777 --directory cache
install --mode 2777 --directory log
docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=mediawiki/extensions/PoolCounter \
    --env ZUUL_REF=master \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/log://log \
    docker-registry.wikimedia.org/releng/rake-poolcounter:latest
