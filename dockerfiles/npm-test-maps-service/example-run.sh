#!/bin/bash

set -eux -o pipefail

err=""
for repo in kartotherian tilerator; do
    install --mode 777 --directory cache {log,src}"-$repo"
    (cd src"-$repo"
     git init
     git fetch --quiet --depth 1 "https://gerrit.wikimedia.org/r/maps/$repo" "master"
     git checkout FETCH_HEAD
    )

    docker run \
        --rm --tty \
        --env JENKINS_URL=1 \
        --volume /"$(pwd)/log-$repo"://var/lib/jenkins/log \
        --volume /"$(pwd)"/cache://cache \
        --volume /"$(pwd)/src-$repo"://src \
        docker-registry.wikimedia.org/releng/npm-test-maps-service:latest || {
            err="$err$repo failed "
        }
done
if [ -n "$err" ]; then
    echo "Tests failed: $err"
    exit 1
fi
