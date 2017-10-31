#!/bin/bash

set -euxo pipefail

LOG_DIR=/log
export LOG_DIR

capture_logs() {
    mv /src/.tox/*/log/*.log "${LOG_DIR}" || /bin/true
    mv /src/.tox/log "${LOG_DIR}" || /bin/true
}

trap capture_logs EXIT

cd /src

git init
git fetch --depth 2 --quiet "${ZUUL_URL}/${ZUUL_PROJECT}" "$ZUUL_REF"
git checkout --quiet FETCH_HEAD
git submodule --quiet update --init --recursive

# Run tests
TOX_TESTENV_PASSENV="PY_COLORS XDG_CACHE_HOME SPARK_HOME" PY_COLORS=1 SPARK_HOME=/opt/spark-2.1.0-bin-hadoop2.6 tox -v | tee "${LOG_DIR}/stdout.log"
