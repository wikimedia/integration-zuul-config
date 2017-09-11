#!/usr/bin/env bash
# Use this file to rebuild all docker images in this repository
# and tag them with the current timestamp in the format 'vY.m.d.H.M'

set -eu

DOCKER_TAG_DATE='v'`date +%Y.%m.%d.%H.%M`
DOCKER_HUB_ACCOUNT=wmfreleng

info() {
    printf "[$(tput setaf 3)INFO$(tput sgr 0)] %b\n" "$@"
}

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for dockerbuild in "$BASE_DIR"/contint-*/Dockerfile; do
    CONTAINER_DIR="${dockerbuild%/*}"
    CONTAINER_NAME="${CONTAINER_DIR##*/}"

    TAGGED_IMG="${DOCKER_HUB_ACCOUNT}/${CONTAINER_NAME:8}:${DOCKER_TAG_DATE}"

    pushd "$CONTAINER_DIR" &>/dev/null
    info "BUILDING $TAGGED_IMG"

    # This is copied in Dockerfile to ensure that a build step grabs a fresh
    # copy of the git repo when this script is run rather than using a layer
    # from the local Docker cache.
    date --iso=ns > .cache-buster

    docker build \
        -t "${TAGGED_IMG}" \
        -f "Dockerfile" .

    popd &>/dev/null
done
