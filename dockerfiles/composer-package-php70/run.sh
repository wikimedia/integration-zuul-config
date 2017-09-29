#!/usr/bin/env bash

cd /src

git init
git fetch --quiet --depth 1 "${ZUUL_URL}/${ZUUL_PROJECT}" "$ZUUL_REF"
git checkout FETCH_HEAD
git submodule --quiet update --init --recursive

/srv/composer/vendor/bin/composer install --no-progress
/srv/composer/vendor/bin/composer test
