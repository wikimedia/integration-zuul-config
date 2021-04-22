#!/bin/bash

set -euxo pipefail

install --mode 2777 --directory cache
install --mode 2777 --directory log
docker run \
    --rm --tty \
    --env JENKINS_URL=1 \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=mediawiki/vagrant \
    --env ZUUL_REF=refs/changes/03/403403/2 \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/log://log \
    docker-registry.wikimedia.org/releng/rake-vagrant-ruby2.5:latest
