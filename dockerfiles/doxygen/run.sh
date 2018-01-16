#!/usr/bin/env bash

umask 002

set -euxo pipefail

doxygen --version
cd /src
exec doxygen
