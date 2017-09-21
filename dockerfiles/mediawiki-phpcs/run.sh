#!/usr/bin/env bash

cd /src

git init
git fetch --depth 1 "${ZUUL_URL}/${ZUUL_PROJECT}" "$ZUUL_REF"
git checkout FETCH_HEAD
git submodule --quiet update --init --recursive

/srv/composer/vendor/bin/composer install
./vendor/bin/phpcs -p -s --report-full "--report-checkstyle=/log/checkstyle.xml"
