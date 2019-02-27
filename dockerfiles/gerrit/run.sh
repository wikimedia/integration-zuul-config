#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src

bazel version

# Setting home dir for Gerrit tools/download_file.py which uses ~ for caching
# downloaded artifacts
export HOME="$XDG_CACHE_HOME"/gerrithome

# incompatible_string_join_requires_strings=false is due to Bazel 0.27.0
# https://github.com/bazelbuild/bazel/issues/7802
bazel build \
    --incompatible_string_join_requires_strings=false \
    release
