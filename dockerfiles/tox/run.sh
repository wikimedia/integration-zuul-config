#!/bin/bash

set -euxo pipefail

LOG_DIR=/log
export LOG_DIR

capture_logs() {
    mv /src/.tox/*/log/*.log "${LOG_DIR}" || /bin/true
    mv /src/.tox/log "${LOG_DIR}" || /bin/true
}

fix_cache_permissions() {
    # CI runs has nobody:wikidev and the docker host would need access to
    # files. pip creates its cache with restrictive permissions.
    find "$XDG_CACHE_HOME" -type d -not -perm '/g+rx' -print0|xargs -0 --no-run-if-empty chmod g+rx
    find "$XDG_CACHE_HOME" -type f -not -perm '/g+r' -print0|xargs -0 --no-run-if-empty chmod g+r
}

handle_exit() {
    capture_logs
    fix_cache_permissions
}

trap handle_exit EXIT

cd /src

git init
git fetch --depth 2 --quiet "${ZUUL_URL}/${ZUUL_PROJECT}" "$ZUUL_REF"
git checkout --quiet FETCH_HEAD
git submodule --quiet update --init --recursive

# Run tests
TOX_TESTENV_PASSENV="PY_COLORS XDG_CACHE_HOME" PY_COLORS=1 tox -v | tee "${LOG_DIR}/stdout.log"
