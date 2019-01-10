#!/bin/bash

set -eu

_dir="$(dirname "$0")"
_repodir="$(realpath "$_dir/..")"
unset _dir

ZUUL_SERVER_BIN=zuul-server
if [ ! -v TOX_ENV_DIR ]; then
    echo "Setting up zuul_tests tox environment"
    tox -e zuul_tests --notest
    ZUUL_SERVER_BIN="$_repodir"/.tox/zuul_tests/bin/zuul-server
fi
unset _repodir

export ZUUL_SERVER_BIN
