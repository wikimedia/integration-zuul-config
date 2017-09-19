#!/bin/bash

# Note: this example currently has lots of issues and outputs a big long log
docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=analytics/wmde/WDCM \
    --env ZUUL_COMMIT=ccbad554b1fbef3c64893581996104ad70f75b87 \
    --env ZUUL_REF=refs/changes/17/376217/2 \
    --volume /$(pwd)/log://log \
     wmfreleng/lintr:latest
