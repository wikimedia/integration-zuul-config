#!/bin/bash

set -euxo pipefail

# Has to be in the same directory as in Dockerfile.build because of tox caching
PUPPET_DIR="/tmp/cache/puppet"

LOG_DIR="$HOME/log"

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

# Run tests
bundle exec rake test | tee "${LOG_DIR}/rake.log"
