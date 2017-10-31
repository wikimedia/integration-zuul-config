#!/bin/bash

for project in analytics/quarry/web wikimedia/fundraising/tools; do
    docker run \
        --rm --tty \
        --env ZUUL_URL=https://gerrit.wikimedia.org/r \
        --env ZUUL_PROJECT="$project" \
        --env ZUUL_COMMIT=master \
        --env ZUUL_REF=master \
         wmfreleng/tox:latest
done
