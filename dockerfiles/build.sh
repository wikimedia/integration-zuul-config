#!/usr/bin/env bash
# Use this file to rebuild all docker images in this repository

set -eu

info() {
    printf "[$(tput setaf 3)INFO$(tput sgr 0)] %b\n" "$@"
}

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DOCKER_HUB_USER=wmfreleng

for dockerbuild in "$BASE_DIR"/contint-*/Dockerfile; do
    CONTAINER_DIR="${dockerbuild%/*}"
    CONTAINER_NAME="${CONTAINER_DIR##*/}"

    IMG_TAG="${DOCKER_HUB_USER}/${CONTAINER_NAME:8}"

    BUILD_IMG_TAG="${IMG_TAG}-img"
    BUILD_CONTAINER_TAG="${CONTAINER_NAME:8}-build"

    pushd "$CONTAINER_DIR" &>/dev/null
    pushd "$CONTAINER_DIR" &>/dev/null
    info "BUILDING $CONTAINER_NAME"

    docker build \
        -t "${IMG_TAG}" \
        -f "Dockerfile" .

    popd &>/dev/null
done
