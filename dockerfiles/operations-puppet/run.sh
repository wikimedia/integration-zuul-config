#!/bin/bash

set -euxo pipefail

RAKE_TARGET=${RAKE_TARGET:-test}

LOG_DIR="/srv/workspace/log"
export LOG_DIR

capture_logs() {
    # Save logs
    mv "${PUPPET_DIR}"/.tox/*/log/*.log "${LOG_DIR}/" || /bin/true
    mv "${PUPPET_DIR}"/.tox/log/* "${LOG_DIR}/" || /bin/true
}

trap capture_logs EXIT

cd "$PUPPET_DIR"

# Prepare patch set from zuul merger
git remote add zuul "${ZUUL_URL}/${ZUUL_PROJECT}"
git pull --quiet zuul production
git fetch --quiet zuul "$ZUUL_REF"
git checkout --quiet FETCH_HEAD
git submodule --quiet update --init --recursive

# Update bundle if gemfile changed
if git diff --name-only docker-head Gemfile | grep -q 'Gemfile'; then
    bundle update
fi;

# To force color output on non tty
export TOX_TESTENV_PASSENV='PY_COLORS'
export PY_COLORS=1
export SPEC_OPTS='--tty'

# Run tests
bundle exec rake "${RAKE_TARGET}" | tee "${LOG_DIR}/rake.log"
