#!/bin/bash

set -eux -o pipefail

install --mode 777 --directory log cache src
cd src
git init
git fetch --quiet --depth 1 "https://gerrit.wikimedia.org/r/mediawiki/services/trending-edits" "master"
git checkout FETCH_HEAD
cd ..

docker run \
    --rm --tty \
    --env JENKINS_URL=1 \
    --volume /"$(pwd)"/log://var/lib/jenkins/log \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/src://src \
    docker-registry.wikimedia.org/releng/npm-test-librdkafka:latest
