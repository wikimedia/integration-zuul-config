#!/bin/bash

docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=mediawiki/extensions/ElectronPdfService \
    --env ZUUL_COMMIT=d016986bda3bec88bf246fa5c34be2941c54ba70 \
    --env ZUUL_REF=refs/changes/08/371108/4 \
    --env EXT_DEPENDENCIES=mediawiki/extensions/BetaFeatures \
    --entrypoint "bash" \
    wmfreleng/ci-src-setup:latest \
    //srv/setup-mwext.sh
