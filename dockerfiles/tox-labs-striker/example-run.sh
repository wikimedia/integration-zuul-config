#!/bin/bash

set -eu

install --mode 777 --directory log cache

projects=(labs/striker labs/tools/ldap)

for project in "${projects[@]}"; do
    printf "=== Running for %s ====\n" "$project"
    docker run \
        --rm --tty \
        --env JENKINS_URL=1 \
        --env ZUUL_URL=https://gerrit.wikimedia.org/r \
        --env ZUUL_PROJECT=labs/striker \
        --env ZUUL_COMMIT=master \
        --env ZUUL_REF=master \
        --volume /"$(pwd)"/log://log \
        --volume /"$(pwd)"/cache://cache \
        docker-registry.wikimedia.org/releng/tox-labs-striker:latest
done;
echo "Successfully ran examples."
