#!/bin/bash

mkdir -m 777 -p cache log

docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=utfnormal \
    --env ZUUL_REF=master \
    --volume "/$(pwd)/cache"://var/lib/jenkins/cache \
    --volume "/$(pwd)/log"://var/lib/jenkins/log \
    wmfreleng/composer-package:latest
rm -rf cache log
