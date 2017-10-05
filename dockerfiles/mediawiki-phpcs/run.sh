#!/usr/bin/env bash

cd /src

git init
git fetch --quiet --depth 1 "${ZUUL_URL}/${ZUUL_PROJECT}" "$ZUUL_REF"
git checkout --quiet FETCH_HEAD

composer install --no-progress
./vendor/bin/phpcs -p -s --report-full "--report-checkstyle=/log/checkstyle.xml"
