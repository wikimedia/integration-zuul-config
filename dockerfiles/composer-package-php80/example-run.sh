#!/bin/bash

set -eux -o pipefail

mkdir -m 777 -p cache
mkdir -m 777 -p log
mkdir -m 777 -p src
(
cd src
git init
git fetch --quiet --depth 1 "https://gerrit.wikimedia.org/r/utfnormal" "master"
git checkout FETCH_HEAD
)

mkdir -p log
docker run \
    --rm --tty \
    --volume "/$(pwd)/cache://cache" \
    --volume "/$(pwd)/log://var/lib/jenkins/log" \
    --volume "/$(pwd)/src://src" \
    docker-registry.wikimedia.org/releng/composer-package-php80:latest
