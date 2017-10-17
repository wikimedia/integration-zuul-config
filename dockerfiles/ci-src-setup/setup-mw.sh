#!/bin/bash -eu

set -euxo pipefail

umask 002

zuul-cloner --version
zuul-cloner \
            --color \
            --verbose \
            --map /srv/deployment/integration/slave-scripts/etc/zuul-clonemap.yaml \
            --workspace /src \
            --cache-dir /srv/git \
            https://gerrit.wikimedia.org/r/p \
            mediawiki/core

cd /src

[[ -f "composer.json" ]] || exit 0
composer update --ansi --no-progress --prefer-dist --profile -v
