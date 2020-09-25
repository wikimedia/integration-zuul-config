#!/usr/bin/env bash

set -euxo pipefail

umask 002

SOURCE_ROOT="$1"
shift

cd "$SOURCE_ROOT"

# Bypass expensive Symfony\Component\Console\Terminal::getWidth() (T219114#5084302)
export COLUMNS=80

exec vendor/bin/phan -d . --long-progress-bar "$@" --require-config-exists
