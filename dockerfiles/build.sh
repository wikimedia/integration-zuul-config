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
    info "BUILDING $CONTAINER_NAME"

    # Run a standard build step if there is one
    if [[ -f "Dockerfile.build" ]]; then
        info "...Creating build image ${BUILD_IMG_TAG}"
        touch .cache-buster
        docker build \
            -t "${BUILD_IMG_TAG}" \
            -f "Dockerfile.build" .

        info "...Creating build container ${BUILD_CONTAINER_TAG} from ${BUILD_IMG_TAG}"

        # Remove any container that may exist with that container name first
        docker rm $BUILD_CONTAINER_TAG || /bin/true

        docker create --name "${BUILD_CONTAINER_TAG}" "${BUILD_IMG_TAG}"

        # Make sure to purge old cache before making new one
        if [[ -d "cache" ]]; then
            info "...Purging old 'cache'"
            rm -rf "cache"
        fi

        info "...Copying ${BUILD_CONTAINER_TAG}:/tmp/cache artifact to 'cache'"
        docker cp "${BUILD_CONTAINER_TAG}:/tmp/cache" cache
    fi

    info "...Creating final image ${IMG_TAG}"
    docker build \
        -t "${IMG_TAG}" \
        -f "Dockerfile" .

    popd &>/dev/null
done
