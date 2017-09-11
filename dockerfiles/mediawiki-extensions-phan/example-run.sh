#!/bin/bash

docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=mediawiki/extensions/TwoColConflict \
    --env ZUUL_COMMIT=eb57a0fb7be92ba8006dcb14322ff14c79fe12ec \
    --env ZUUL_REF=refs/changes/16/371416/1 \
    --env EXT_DEPENDENCIES="mediawiki/extensions/BetaFeatures\nmediawiki/extensions/WikiEditor" \
    --volume /$(pwd)/log://var/lib/jenkins/log \
     wmfreleng/mediawiki-extensions-phan:latest