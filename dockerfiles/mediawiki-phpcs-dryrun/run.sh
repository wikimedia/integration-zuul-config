#!/bin/bash

set -euxo pipefail


cd src/
# Update mediawiki/core
git pull
composer update
cd vendor/mediawiki/mediawiki-codesniffer

# Prepare patch set from zuul merger
git remote add zuul "${ZUUL_URL}/${ZUUL_PROJECT}"
git fetch --quiet zuul "$ZUUL_REF"
git checkout --quiet FETCH_HEAD

cd /src
./vendor/bin/phpcs -sp
