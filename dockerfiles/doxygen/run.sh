#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src

git init
git fetch --depth 2 --quiet "${ZUUL_URL}/${ZUUL_PROJECT}" "$ZUUL_REF"
git checkout --quiet FETCH_HEAD
git submodule --quiet update --init --recursive

doxygen --version
exec doxygen
