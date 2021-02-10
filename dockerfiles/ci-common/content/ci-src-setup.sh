#!/usr/bin/env bash
#
# See also coverage tests in dockerfiles/tests/test_ci_common.py
#

umask 002

set -euxo pipefail

if [[ "${JENKINS_URL:-}" == "" && "${CI:-}" == "" ]]; then
    echo "Skipping git clone, not running on CI env (JENKINS_URL and CI vars empty/unset)."
    exit
fi

git init
git fetch --quiet --update-head-ok --depth 2 "${ZUUL_URL}/${ZUUL_PROJECT}" "+${ZUUL_REF}:${ZUUL_REF}"

if [[ "${ZUUL_BRANCH:-}" == "" ]]; then
    # For ref-updated events such as a new tag
    git checkout -q FETCH_HEAD
else
    git checkout -B "$ZUUL_BRANCH" FETCH_HEAD
fi

set +x
if [[ "${GIT_NO_SUBMODULES:-}" == "" ]]; then
    set -x
    git submodule --quiet update --init --recursive
else
    echo "\$GIT_NO_SUBMODULES set, skipping submodules"
fi
