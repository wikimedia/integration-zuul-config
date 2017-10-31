#!/bin/bash

install --mode 777 --directory log cache

docker run \
    --rm --tty \
    --env JENKINS_URL=1 \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=search/MjoLniR \
    --env ZUUL_COMMIT=e4d4c798a9a7821eb48788cdfeb8de0a12a75d44 \
    --env ZUUL_REF=refs/changes/31/387831/4 \
    --volume /"$(pwd)"/log://log \
    --volume /"$(pwd)"/cache://cache \
     wmfreleng/tox-pyspark:latest
