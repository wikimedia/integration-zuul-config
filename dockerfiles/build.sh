#!/usr/bin/env bash
# Use this file to rebuild all docker images in this repository
# and tag them with the current timestamp in the format 'vY.m.d.H.M'

set -eu

DOCKER_TAG_DATE='v'`date --utc +%Y.%m.%d.%H.%M`
DOCKER_HUB_ACCOUNT=wmfreleng

info() {
    printf "[$(tput setaf 3)INFO$(tput sgr 0)] %b\n" "$@"
}

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for dockerbuild in "$BASE_DIR"/contint-*/Dockerfile; do
    CONTAINER_DIR="${dockerbuild%/*}"
    CONTAINER_NAME="${CONTAINER_DIR##*/}"

    IMG="${DOCKER_HUB_ACCOUNT}/${CONTAINER_NAME:8}"
    TAGGED_IMG="${IMG}:${DOCKER_TAG_DATE}"

    pushd "$CONTAINER_DIR" &>/dev/null
    info "BUILDING $TAGGED_IMG"

    if [ -f "./prebuild.sh" ]
    then
        ./prebuild.sh
    fi

    docker build \
        -t "${TAGGED_IMG}" \
        -f "Dockerfile" .

    docker tag "${TAGGED_IMG}" "${IMG}:latest"

    popd &>/dev/null
done
