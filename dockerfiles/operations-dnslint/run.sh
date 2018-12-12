#!/bin/bash

set -euxo pipefail

pushd "$DNSDIR"

# Prepare patch set from zuul merger
git remote add zuul "${ZUUL_URL}/${ZUUL_PROJECT}"
git pull --quiet zuul master
git fetch --quiet zuul "$ZUUL_REF"
git checkout --quiet FETCH_HEAD


# Run tests
./utils/run-tests.sh
