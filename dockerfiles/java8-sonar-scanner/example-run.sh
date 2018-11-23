#!/bin/bash

docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r/p \
    --env ZUUL_PROJECT=mediawiki/extensions/GrowthExperiments \
    --env ZUUL_COMMIT=master \
    --env ZUUL_REF=master \
    --volume /"$(pwd)"://src \
    docker-registry.wikimedia.org/releng/java8-sonar-scanner \
        -Dsonar.host.url=https://sonarqube.wikimedia.org
