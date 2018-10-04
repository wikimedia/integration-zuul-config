#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src

git init
git fetch --quiet --depth 2 "${ZUUL_URL}/${ZUUL_PROJECT}" "$ZUUL_REF"
git checkout FETCH_HEAD

set +x
if [ -z "${GIT_NO_SUBMODULES:-}" ]; then
    set -x
    git submodule --quiet update --init --recursive
else
    echo "\$GIT_NO_SUBMODULES set, skipping submodules"
fi
