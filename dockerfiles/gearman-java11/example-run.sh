#!/bin/bash

install --mode 777 --directory cache log src

docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=integration/gearman-java \
    --env ZUUL_COMMIT=master \
    --env ZUUL_REF=master \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/log://log \
    --volume /"$(pwd)"/src://src \
    docker-registry.wikimedia.org/releng/gearman-java11:latest \
        clean verify
