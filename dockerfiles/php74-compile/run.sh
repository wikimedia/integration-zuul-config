#!/usr/bin/env bash

set -euxo pipefail

umask 002

cd src/
phpize --version
phpize
# Work around libtool version mismatch
autoreconf -i
./configure
make
REPORT_EXIT_STATUS=1 make test

