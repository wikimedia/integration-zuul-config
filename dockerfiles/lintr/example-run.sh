#!/bin/bash

# Note: this example currently has lots of issues and outputs a big long log
docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=analytics/wmde/WDCM \
    --env ZUUL_COMMIT=7c680069cfb5b1511826f35ce4a2c29598507ec6 \
    --env ZUUL_REF=refs/changes/06/380306/2 \
    --volume /$(pwd)/log://log \
     wmfreleng/lintr:latest
