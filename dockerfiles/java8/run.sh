#!/bin/bash

set -euxo pipefail

umask 002

cd /src

git init
git fetch --depth 2 --quiet "${ZUUL_URL}/${ZUUL_PROJECT}" "$ZUUL_REF"
git checkout --quiet -b "${ZUUL_BRANCH}" FETCH_HEAD
git submodule --quiet update --init --recursive

exec /usr/local/bin/mvn "${@}"
