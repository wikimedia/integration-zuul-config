#!/usr/bin/env bash
# Use this file to rebuild all docker images in this repository

set -eu

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

wget -O "$BASE_DIR/share/wikimedia-archive-keyring.gpg" \
    http://apt.wikimedia.org/autoinstall/keyring/wikimedia-archive-keyring.gpg

for dockerbuild in "$BASE_DIR"/contint-*/Dockerfile; do
    CONTAINER_DIR="${dockerbuild%/*}"
    CONTAINER_NAME="${CONTAINER_DIR##*/}"
    docker build -t contint/"${CONTAINER_NAME:8}" -f "${dockerbuild}" "$BASE_DIR"
done

rm -rf "$BASE_DIR/share/wikimedia-archive-keyring.gpg" \
