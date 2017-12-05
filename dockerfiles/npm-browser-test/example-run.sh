#!/bin/bash

set -euo pipefail

mkdir -m 777 -p log
mkdir -m 777 -p src
mkdir -m 777 -p cache

docker run \
    --rm --tty \
    --volume /"$(pwd)"/src://src \
    -e ZUUL_URL=https://gerrit.wikimedia.org/r/ \
    -e ZUUL_PROJECT=VisualEditor/VisualEditor \
    -e ZUUL_REF=master \
    wmfreleng/ci-src-setup-simple:v2017.10.28.06.19

docker run \
    --rm --tty \
    --volume /"$(pwd)"/log://var/lib/jenkins/log \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/log://log \
    --volume /"$(pwd)"/src://src \
     wmfreleng/npm-browser-test:latest
rm -rf log
