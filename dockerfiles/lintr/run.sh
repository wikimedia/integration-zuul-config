#!/bin/bash

set -euxo pipefail

LOG_DIR="/log"
export LOG_DIR

cd "/src"

# Prepare patch set from zuul merger
git init
git fetch --quiet --depth 2 "${ZUUL_URL}/${ZUUL_PROJECT}" "${ZUUL_REF}"
git checkout --quiet FETCH_HEAD

Rscript /lint.R | tee /log/lintr.log