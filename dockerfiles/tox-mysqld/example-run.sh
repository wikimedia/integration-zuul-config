#!/bin/bash

install --mode 777 --directory log cache

# XXX note wikimedia/fundraising/tools test suite expects the Jenkins env
# variable EXECUTOR_NUMBER to be set.

docker run \
    --rm --tty \
    --env EXECUTOR_NUMBER=1 \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=wikimedia/fundraising/tools \
    --env ZUUL_COMMIT=master \
    --env ZUUL_REF=master \
    --volume /"$(pwd)"/log://log \
    --volume /"$(pwd)"/cache://cache \
    docker-registry.wikimedia.org/releng/tox-mysqld:0.1.0
