#!/usr/bin/env bash

set -euxo pipefail

# Has to be in the same directory as in Dockerfile.build because of tox caching
PUPPET_DIR="/tmp/cache/puppet"

LOG_DIR="$HOME/log"
CACHE_DIR="$HOME/.cache"

capture_logs() {
    # Save logs
    mv "${PUPPET_DIR}"/.tox/*/log/*.log "${LOG_DIR}/" || /bin/true
    mv "${PUPPET_DIR}"/.tox/log/* "${LOG_DIR}/" || /bin/true
}

trap capture_logs EXIT

mkdir -p /tmp/cache

mv "${CACHE_DIR}/puppet" "$PUPPET_DIR"
cd "$PUPPET_DIR"

# Prepare patch set from zuul merger
git remote add zuul "${ZUUL_URL}/${ZUUL_PROJECT}"
git pull --quiet zuul production
git fetch --quiet zuul "$ZUUL_REF"
git checkout --quiet FETCH_HEAD
git submodule --quiet update --init --recursive

# Tox setup
mv "${CACHE_DIR}/tox" '.tox'

# Bundle setup
mkdir -p .bundle
cat <<BUNDLE > .bundle/config
---
BUNDLE_PATH: "/var/lib/jenkins/.cache/bundle"
BUNDLE_CLEAN: true
BUNDLE_DISABLE_SHARED_GEMS: '1'
BUNDLE

# Run tox tests
{
    set -o pipefail
    PY_COLORS=1 tox -v | tee "${LOG_DIR}/tox.log"
    set +o pipefail
} &
PID_ONE=$!

# Run rake tests
{
    set -o pipefail
    bundle exec rake test | tee "${LOG_DIR}/rake.log"
    set +o pipefail
} &
PID_TWO=$!

set +e
wait $PID_ONE
EXIT_ONE=$?

wait $PID_TWO
EXIT_TWO=$?
set -e

# Exit non-zero if any subcommand exited non-zero
(( EXIT_ONE == 0 )) || exit 1
(( EXIT_TWO == 0 )) || exit 2
