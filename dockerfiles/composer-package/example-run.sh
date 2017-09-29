#!/bin/bash

install --mode 777 --directory log
docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=utfnormal \
    --env ZUUL_COMMIT=668604441afd899efb073ce4c6b5545341ef6582 \
    --env ZUUL_REF=refs/changes/57/375857/1 \
    --volume /$(pwd)/log://var/lib/jenkins/log \
     wmfreleng/composer-package:latest
