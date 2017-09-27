#!/bin/bash

install --mode 777 --directory log
docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=analytics/quarry/web \
    --env ZUUL_COMMIT=a6173a23ae90dddef446eeea02019b685228e7ea \
    --env ZUUL_REF=refs/changes/43/377043/1 \
    --volume /"$(pwd)"/log://log \
     wmfreleng/tox:latest
