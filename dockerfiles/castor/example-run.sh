#!/bin/bash

set -e

function assert() {
    expected=$1
    shift

    exec 3>&1
    actual=$("$@"|tee >(cat - >&3))

    if [ "$expected" = "$actual" ]; then
        echo "[OK] $expected"
    else
        echo "[FAILED] $expected"
        colordiff -u <(echo "$expected") <(echo "$actual")
    fi
}

assert $'Defined: CASTOR_NAMESPACE="mediawiki-core/master/dosomething"\r' docker run \
    --rm --tty \
    --env ZUUL_PROJECT=mediawiki/core \
    --env ZUUL_BRANCH=master \
    --env JOB_NAME=dosomething \
    wmfreleng/castor:latest \
    config
