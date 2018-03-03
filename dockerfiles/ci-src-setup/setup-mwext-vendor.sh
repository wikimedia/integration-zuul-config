#!/bin/bash -eu
# Clones repositories into the right place, and creates /src/extensions_load.txt.
set -euxo pipefail

umask 002

echo $ZUUL_PROJECT > /tmp/deps.txt
echo -e "${EXT_DEPENDENCIES:-}" >> /tmp/deps.txt
echo -e "${SKIN_DEPENDENCIES:-}" > /tmp/deps_skins.txt

cd /src

zuul-cloner --version
zuul-cloner \
            --color \
            --verbose \
            --map /srv/deployment/integration/slave-scripts/etc/zuul-clonemap.yaml \
            --workspace /src \
            --cache-dir /srv/git \
            https://gerrit.wikimedia.org/r/p \
            mediawiki/core \
            mediawiki/vendor \
            $(cat /tmp/deps.txt) \
            $(cat /tmp/deps_skins.txt)

find extensions skins -maxdepth 2 \
            -name .gitmodules \
            -execdir bash -xe -c '
                git submodule foreach git clean -xdff -q
                git submodule update --init --recursive
                git submodule status
                ' \;

cp /tmp/deps.txt > /src/extensions_load.txt
