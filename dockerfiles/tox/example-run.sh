#!/bin/bash

install --mode 777 --directory cache log
docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=integration/config \
    --env ZUUL_COMMIT=master \
    --env ZUUL_REF=master \
    --volume /"$(pwd)"/log://log \
    --volume /"$(pwd)"/cache://cache \
     wmfreleng/tox:latest
