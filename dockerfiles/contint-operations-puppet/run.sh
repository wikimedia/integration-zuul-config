#!/usr/bin/env bash

set -eux

TEMP_DIR=$(mktemp -d)
LOG_DIR="$HOME/.cache/log"

git clone \
    --reference "/srv/git/${ZUUL_PROJECT}.git" \
    "$ZUUL_URL/$ZUUL_PROJECT" \
    "$TEMP_DIR/puppet"

cd "$TEMP_DIR/puppet"

git fetch origin $ZUUL_REF
git checkout FETCH_HEAD

# Run tox tests
{
    set -o pipefail
    PY_COLORS=1 tox -v | tee "${LOG_DIR}/tox.log"
    set +o pipefail
} &
PID_ONE=$!

# Run rake tests
{
    bundle install --path "${HOME}/.gems" --clean
    bundle exec rake test | tee "${LOG_DIR}/rake.log"
} &
PID_TWO=$!

wait $PID_ONE
EXIT_ONE=$?

wait $PID_TWO
EXIT_TWO=$?

# Save logs
mv "${TEMP_DIR}"/puppet/.tox/*/log/*.log "${LOG_DIR}/" || /bin/true
mv "${TEMP_DIR}"/puppet/.tox/log/* "${LOG_DIR}/" || /bin/true

# Exit non-zero if any subcommand exited non-zero
(( EXIT_ONE == 0 )) || exit 1
(( EXIT_TWO == 0 )) || exit 2
