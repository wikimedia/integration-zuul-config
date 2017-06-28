#!/usr/bin/env bash

set -euxo pipefail

TEMP_DIR=$(mktemp -d)
LOG_DIR="$HOME/log"
CACHE_DIR="$HOME/.cache"

capture_logs() {
    # Save logs
    mv "${TEMP_DIR}"/puppet/.tox/*/log/*.log "${LOG_DIR}/" || /bin/true
    mv "${TEMP_DIR}"/puppet/.tox/log/* "${LOG_DIR}/" || /bin/true
}

trap capture_logs EXIT

git clone \
    --quiet \
    --reference "/srv/git/${ZUUL_PROJECT}.git" \
    "$ZUUL_URL/$ZUUL_PROJECT" \
    "$TEMP_DIR/puppet"

cd "$TEMP_DIR/puppet"

git fetch --quiet origin $ZUUL_REF
git checkout --quiet FETCH_HEAD
git submodule --quiet update --init --recursive

[ -d /cache/.cache ] && {
    mkdir -p "$CACHE_DIR"
    cp -R /cache/.cache/* "${CACHE_DIR}/"
}

# Run tox tests
{
    set -o pipefail
    PY_COLORS=1 tox -v | tee "${LOG_DIR}/tox.log"
    set +o pipefail
} &
PID_ONE=$!

# Run rake tests
{
    bundle install --clean
    bundle exec rake test | tee "${LOG_DIR}/rake.log"
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
