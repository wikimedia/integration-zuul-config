#!/bin/bash
#
# Generate coverage for a MediaWiki extension
# Copyright (C) 2017-2018 Kunal Mehta <legoktm@member.fsf.org>
# Copyright (C) 2018 Antoine Musso <hashar@free.fr>
#
# Requires ZUUL_PROJECT to be set.
#
# Also require environment variables set by Quibble:
# - LOG_DIR
# - MW_INSTALL_PATH
# - WORKSPACE
#
# Outputs:
# - clover.xml in $LOG_DIR
# - HTML report in $WORKSPACE/cover

set -eux -o pipefail

EXT_NAME=$(basename "$ZUUL_PROJECT")

# Edit suite.xml to use the proper coverage paths
phpunit-suite-edit "$MW_INSTALL_PATH/tests/phpunit/suite.xml" --cover-extension "$EXT_NAME"

mkdir -p "$WORKSPACE"/cover
find "$WORKSPACE"/cover -mindepth 1 -delete

function relay_signals() {
    for signal ; do
        trap 'kill -$signal $cover_pid; wait $cover_pid' "$signal"
    done
}

# Some tests might fail, we still want to be able to publish the coverage
# report for those that passed.
set +e
php7.0 -d zend_extension=xdebug.so \
    "$MW_INSTALL_PATH"/tests/phpunit/phpunit.php \
    --testsuite extensions \
    --coverage-clover "$LOG_DIR"/clover.xml \
    --coverage-html "$WORKSPACE"/cover \
    "$MW_INSTALL_PATH/extensions/$EXT_NAME/tests/phpunit" &
cover_pid=$!
relay_signals SIGINT SIGTERM
wait "$cover_pid"
set -e


# But bails out if no HTML coverage report has been generated
test -f "$WORKSPACE"/cover/index.html

if [ -s "$LOG_DIR"/clover.xml ]; then
    cp "$LOG_DIR"/clover.xml "$WORKSPACE"/cover/clover.xml
fi
