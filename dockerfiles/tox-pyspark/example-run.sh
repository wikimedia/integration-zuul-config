#!/bin/bash

install --mode 777 --directory log cache

docker run \
    --rm --tty \
    --env JENKINS_URL=1 \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=search/MjoLniR \
    --env ZUUL_COMMIT=refs/changes/03/410403/1 \
    --env ZUUL_REF=refs/changes/03/410403/1 \
    --volume /"$(pwd)"/log://log \
    --volume /"$(pwd)"/cache://cache \
    docker-registry.wikimedia.org/releng/tox-pyspark:0.1.0
