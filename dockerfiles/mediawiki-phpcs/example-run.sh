#!/bin/bash

install --mode 777 --directory log
docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=mediawiki/core \
    --env ZUUL_COMMIT=e447a97de58e9e2b4dd6a6e31a91edc68dde1217 \
    --env ZUUL_REF=refs/changes/52/378752/2 \
    --volume /$(pwd)/log://var/lib/jenkins/log \
     wmfreleng/mediawiki-phpcs:latest
