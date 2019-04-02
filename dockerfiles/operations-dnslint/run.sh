#!/bin/bash

set -ex

# Case 1: if there is a /src directory with a clone of the
# operations/dns repository, work there
if [[ -d /src/.git ]]; then
    pushd /src
# Case 2: running on a submitted change - typically in CI
elif [[ -n "$ZUUL_REF" ]]; then
    pushd "$DNSDIR"
    # Prepare patch set from zuul merger
    git remote add zuul "${ZUUL_URL}/${ZUUL_PROJECT}"
    git pull --quiet zuul master
    git fetch --quiet zuul "$ZUUL_REF"
    git checkout --quiet FETCH_HEAD
else
    echo "If running local tests, please mount the source directory under /src" && exit 1
fi;

# Run tests
TOX_TESTENV_PASSENV="PY_COLORS" PY_COLORS=1 tox
