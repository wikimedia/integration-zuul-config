#!/bin/bash

install --mode 777 --directory log
docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=analytics/quarry/web \
    --env ZUUL_COMMIT=master \
    --env ZUUL_REF=master \
    --volume /"$(pwd)"/log://log \
     wmfreleng/tox-pyspark:latest
