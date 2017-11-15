#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src

git init
git fetch --quiet --depth 1 "${ZUUL_URL}/${ZUUL_PROJECT}" "$ZUUL_REF"
git checkout FETCH_HEAD
git submodule --quiet update --jobs 8 --init --recursive
