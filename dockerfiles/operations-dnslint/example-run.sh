#!/bin/bash

docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=operations/dns \
    --env ZUUL_REF=refs/changes/78/479178/1 \
    docker-registry.wikimedia.org/releng/operations-dnslint:0.0.1
