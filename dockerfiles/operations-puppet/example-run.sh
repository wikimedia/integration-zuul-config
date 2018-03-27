#!/bin/bash

install --mode 777 --directory log
docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=operations/puppet \
    --env ZUUL_COMMIT=72d31ffb0fa612482d268b6f5484785842cd0fda \
    --env ZUUL_REF=refs/changes/49/374349/2 \
    --volume /$(pwd)/log://srv/workspace/log \
    docker-registry.wikimedia.org/releng/operations-puppet:0.3.1
