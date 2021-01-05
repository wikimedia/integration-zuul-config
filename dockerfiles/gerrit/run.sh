#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src

bazelisk version

# Setting home dir for Gerrit tools/download_file.py which uses ~ for caching
# downloaded artifacts
export HOME="$XDG_CACHE_HOME"/gerrithome

bazelisk info
bazelisk build "${@:-release}"
