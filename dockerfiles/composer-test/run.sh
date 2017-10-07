#!/usr/bin/env bash

set -euxo pipefail

cd /src

git init
git fetch --quiet --depth 1 "${ZUUL_URL}/${ZUUL_PROJECT}" "$ZUUL_REF"
git checkout FETCH_HEAD
git submodule --quiet update --init --recursive

composer --ansi validate --no-check-publish
composer install --no-progress --prefer-dist
composer test
