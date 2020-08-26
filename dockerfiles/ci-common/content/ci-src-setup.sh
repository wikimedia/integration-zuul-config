#!/usr/bin/env bash
#
# See also coverage tests in dockerfiles/tests/test_ci_common.py
#

umask 002

set -euxo pipefail

git init
git fetch --quiet --update-head-ok --depth 2 "${ZUUL_URL}/${ZUUL_PROJECT}" "+$ZUUL_REF:$ZUUL_REF"

if [ -z "${ZUUL_BRANCH:-}" ]; then
    # For ref-updated events such as a new tag
    git checkout -q FETCH_HEAD
else
    git checkout -B "$ZUUL_BRANCH" FETCH_HEAD
fi

set +x
if [ -z "${GIT_NO_SUBMODULES:-}" ]; then
    set -x
    git submodule --quiet update --init --recursive
else
    echo "\$GIT_NO_SUBMODULES set, skipping submodules"
fi
