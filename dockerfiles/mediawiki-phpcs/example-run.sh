#!/bin/bash

set -euo pipefail

install --mode 777 --directory cache log src

docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=mediawiki/core \
    --env ZUUL_COMMIT=e447a97de58e9e2b4dd6a6e31a91edc68dde1217 \
    --env ZUUL_REF=refs/changes/52/378752/2 \
    --volume "/$(pwd)/cache://cache" \
    --volume "/$(pwd)/src://src" \
    docker-registry.wikimedia.org/releng/ci-src-setup-simple:latest

docker run \
    --rm --tty \
    --volume "/$(pwd)/cache:/cache" \
    --volume "/$(pwd)/log://var/lib/jenkins/log" \
    --volume "/$(pwd)/src://src" \
    docker-registry.wikimedia.org/releng/mediawiki-phpcs:latest
