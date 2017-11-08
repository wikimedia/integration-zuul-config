#!/bin/bash

set -euxo pipefail

umask 002

LOG_DIR=/log
export LOG_DIR

capture_tox_logs() {
    # XXX unlike `mv`, `cp` does not preserve permissions and hence the
    # destination files will inherit the group thanks to log having setgid.
    cp --recursive /src/.tox/*/log/*.log "${LOG_DIR}" || /bin/true
    cp --recursive /src/.tox/log "${LOG_DIR}" || /bin/true
}

cd /src

git init
git fetch --depth 2 --quiet "${ZUUL_URL}/${ZUUL_PROJECT}" "$ZUUL_REF"
git checkout --quiet FETCH_HEAD
git submodule --quiet update --init --recursive

trap capture_tox_logs EXIT

# Run tests. Pass all environment variables to tox since the environment here
# is already pretty restrictive.
TOX_TESTENV_PASSENV="*" PY_COLORS=1 tox -v
