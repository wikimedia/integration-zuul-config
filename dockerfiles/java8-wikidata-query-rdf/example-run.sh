#!/bin/bash

install --mode 2777 --directory cache
install --mode 2777 --directory log

docker run \
    --rm --tty \
    --env JENKINS_URL=1 \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=wikidata/query/rdf \
    --env ZUUL_COMMIT=master \
    --env ZUUL_REF=master \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/log://log \
    docker-registry.wikimedia.org/releng/java8-wikidata-query-rdf:latest \
        clean verify
