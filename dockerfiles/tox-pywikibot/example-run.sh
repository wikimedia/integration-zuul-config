#!/bin/bash

install --mode 777 --directory log cache

docker run \
    --rm --tty \
    --env JENKINS_URL=1 \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=pywikibot/core \
    --env ZUUL_COMMIT=master \
    --env ZUUL_REF=master \
    --volume /"$(pwd)"/log://log \
    --volume /"$(pwd)"/cache://cache \
     wmfreleng/tox-pywikibot:latest -e nose34
