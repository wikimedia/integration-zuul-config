#!/usr/bin/env bash

set -euxo pipefail

cd /src

git init
git fetch --quiet --depth 1 "${ZUUL_URL}/${ZUUL_PROJECT}" "${ZUUL_REF}"
git checkout --quiet FETCH_HEAD

composer --ansi validate
composer install --no-progress --prefer-dist
composer test
