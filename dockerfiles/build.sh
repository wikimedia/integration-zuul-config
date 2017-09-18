#!/usr/bin/env bash
# Use this file to rebuild all docker images in this repository
# and tag them with the current timestamp in the format 'vY.m.d.H.M'

set -eu

DOCKER_TAG_DATE='v'`date --utc +%Y.%m.%d.%H.%M`
DOCKER_HUB_ACCOUNT=wmfreleng

info() {
    printf "[$(tput setaf 3)INFO$(tput sgr 0)] %b\n" "$@"
}

buildDockerfile() {
    DOCKERFILE=$@
    DOCKERFILE_DIR="${DOCKERFILE%/*}"
    DOCKERFILE_NAME="${DOCKERFILE_DIR##*/}"

    IMG="${DOCKER_HUB_ACCOUNT}/${DOCKERFILE_NAME}"
    TAGGED_IMG="${IMG}:${DOCKER_TAG_DATE}"

    pushd "$DOCKERFILE_DIR" &>/dev/null
    info "BUILDING $TAGGED_IMG"

    if [ -x "./prebuild.sh" ]; then
        ./prebuild.sh
    fi

    docker build \
        -t "${TAGGED_IMG}" \
        -f "Dockerfile" .

    docker tag "${TAGGED_IMG}" "${IMG}:latest"

    rm ./cache-buster-*

    popd &>/dev/null
}

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ $# -eq 0 ]; then
    for DOCKERFILE in "$BASE_DIR"/*/Dockerfile; do
        buildDockerfile $DOCKERFILE
    done
else
    buildDockerfile "${BASE_DIR}/${1%/}/Dockerfile"
fi
