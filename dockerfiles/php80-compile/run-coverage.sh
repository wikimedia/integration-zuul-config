#!/bin/bash

set -euxo pipefail

umask 002

REPORT_PATH=/src/coverage
INFO_FILE=php-extension.info
CFLAGS="-g -O0 --coverage -fprofile-arcs -ftest-coverage"
LDFLAGS="-lgcov"
EXTRA_LDFLAGS="-precious-files-regex \.gcno$"

cd src/
phpize --version
phpize
CFLAGS="$CFLAGS" CXXFLAGS="$CFLAGS" LDFLAGS="$LDFLAGS" EXTRA_LDFLAGS="$EXTRA_LDFLAGS" ./configure

lcov --directory . --zerocounters

make test

lcov --directory . --capture --output-file $INFO_FILE
lcov --remove $INFO_FILE "tests/*" "/usr/*" --output-file $INFO_FILE
genhtml --o $REPORT_PATH -t "${ZUUL_PROJECT} test coverage report" --num-spaces 4 --demangle-cpp $INFO_FILE
