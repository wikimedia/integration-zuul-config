#!/bin/bash -eu

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

echo $ZUUL_PROJECT > /tmp/extensions_load.txt
echo -e "${EXT_DEPENDENCIES:-}" >> /tmp/extensions_load.txt

set -u

composer --ansi validate --no-check-publish
/srv/deployment/integration/slave-scripts/bin/mw-create-composer-local.py "/tmp/extensions_load.txt" composer.local.json
composer update --ansi --no-progress --prefer-dist --profile --no-dev
cd /src/$THING_SUBNAME
composer update --ansi --no-progress --prefer-dist --profile
