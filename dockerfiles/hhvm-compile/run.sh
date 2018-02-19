#!/usr/bin/env bash

set -euxo pipefail

umask 002

cd src/
hhvm --version
hphpize
cmake .
make
phpize  # Generate run-tests.php
REPORT_EXIT_STATUS=1 ./hhvm-test.sh run-tests.php
