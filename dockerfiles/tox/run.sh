#!/bin/bash

set -euxo pipefail

umask 002

LOG_DIR=/log
export LOG_DIR

capture_logs() {
    # XXX unlike `mv`, `cp` does not preserve permissions and hence the
    # destination files will inherit the group thanks to log having setgid.
    #
    # XXX later tox version supports specifying the envs log directory
    #
    cp --recursive /src/.tox/*/log/*.log "${LOG_DIR}" || /bin/true
    cp --recursive /src/.tox/log "${LOG_DIR}" || /bin/true
}

trap capture_logs EXIT

cd /src

git init
git fetch --depth 2 --quiet "${ZUUL_URL}/${ZUUL_PROJECT}" "$ZUUL_REF"
git checkout --quiet FETCH_HEAD
git submodule --quiet update --init --recursive

# Run tests
TOX_TESTENV_PASSENV="PY_COLORS XDG_CACHE_HOME" PY_COLORS=1 tox -v | tee "${LOG_DIR}/stdout.log"
