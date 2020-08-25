#!/usr/bin/env bash

umask 002

set -euxo pipefail

/utils/ci-src-setup.sh

doxygen --version
exec doxygen
