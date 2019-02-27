#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src

bazel version

bazel build release
