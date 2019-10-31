#!/bin/bash

set -euxo pipefail

RAKE_TARGET=${RAKE_TARGET:-test}

LOG_DIR="/srv/workspace/log"
export LOG_DIR

TMP_PUPPET_DIR="/tmp/local-puppet-copy"
export TMP_PUPPET_DIR

capture_logs() {
    # Save logs
    mv "${PUPPET_DIR}"/.tox/*/log/*.log "${LOG_DIR}/" || /bin/true
    mv "${PUPPET_DIR}"/.tox/log/* "${LOG_DIR}/" || /bin/true
}

local_cleanup() {
    rm -rf "$TMP_PUPPET_DIR"
}


execute() {
    # Update bundle if gemfile changed
    if git diff --name-only docker-head Gemfile | grep -q 'Gemfile'; then
        bundle update
    fi;
    # To force color output on non tty
    export TOX_TESTENV_PASSENV='PY_COLORS'
    export PY_COLORS=1
    export SPEC_OPTS='--tty'

    # Run tests
    bundle exec rake "${RAKE_TARGET}" "$@"
}

execute_ci() {
    trap capture_logs EXIT
    cd "$PUPPET_DIR"
    # Prepare patch set from zuul merger
    git remote add zuul "${ZUUL_URL}/${ZUUL_PROJECT}"
    git pull --quiet zuul production
    git fetch --quiet zuul "$ZUUL_REF"
    git checkout --quiet FETCH_HEAD
    execute | tee "${LOG_DIR}/rake.log"
}

execute_local() {
    set +x
    trap local_cleanup exit
    ORIGIN=${ORIGIN:-/src}
    # get a copy of the local working directory
    echo "Copying your working copy to the destination"
    mkdir -p $TMP_PUPPET_DIR && cd $TMP_PUPPET_DIR
    tar --ignore-failed-read -C "$ORIGIN" -c  .  | tar -xf -
    # Copy the tox dir, the bundle dir and Gemfile.lock
    # from the container's puppet directory.
    for what in ".tox" ".bundle" "Gemfile.lock"; do
        rm -rf "${TMP_PUPPET_DIR}/${what}"
        cp -ax "${PUPPET_DIR}/${what}" "${TMP_PUPPET_DIR}/";
    done
    # Reproduce the docker-head tag
    TAG_REF=$(cd "$PUPPET_DIR" && git show-ref docker-head | cut -d\  -f1)
    git tag docker-head "$TAG_REF"
    execute -j 1
}


if [ -n "$ZUUL_REF" ]; then
    execute_ci
else
    # Local copy. Output to stdout and don't capture logs
    execute_local
fi
