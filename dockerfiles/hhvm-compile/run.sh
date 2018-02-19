#!/usr/bin/env bash

set -euxo pipefail

umask 002

hhvm --version
hphpize
cmake .
make
phpize  # Generate run-tests.php
export REPORT_EXIT_STATUS=1
export NO_INTERACTION=1
export TEST_PHP_EXECUTABLE=/usr/bin/hhvm
if [ -f luasandbox.so ]; then
    ./hhvm-test.sh run-tests.php
elif [ -f wikidiff2.so ]; then
    hhvm run-tests.php -d "hhvm.dynamic_extensions[wikidiff2.so]=$(pwd)/wikidiff2.so"
else
    echo "Only supports luasandbox or wikidiff2"
    exit 1
fi
