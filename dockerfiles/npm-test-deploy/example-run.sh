#!/bin/bash

set -eux

mkdir -m 777 -p log
mkdir -m 777 -p src
mkdir -m 777 -p cache

docker run \
    --rm --tty \
    --volume /"$(pwd)"/src://src \
    -e ZUUL_URL=https://gerrit.wikimedia.org/r/ \
    -e ZUUL_PROJECT=mediawiki/services/cxserver/deploy \
    -e ZUUL_REF="master" \
        wmfreleng/ci-src-setup-simple

docker run \
    --rm --tty \
    --volume /"$(pwd)"/log://var/lib/jenkins/log \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/src://src \
         wmfreleng/npm-test-deploy:latest
