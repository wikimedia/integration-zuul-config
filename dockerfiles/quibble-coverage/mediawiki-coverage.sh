#!/bin/bash

set -eux -o pipefail

function relay_signals() {
    for signal ; do
        trap 'kill -$signal $cover_pid; wait $cover_pid' "$signal"
    done
}

# We want to publish code coverage even in case there is a PHPUnit test
# failure. Normal test failures are not fatal and PHPUnit will still
# generate console output, clover reports and html reports.
set +e
php -d zend_extension=xdebug.so \
    tests/phpunit/phpunit.php \
        --exclude-group Dump,Broken,ParserFuzz,Stub \
        --coverage-clover "$LOG_DIR"/clover.xml \
        --coverage-html "$WORKSPACE/cover" &
cover_pid=$!
relay_signals SIGINT SIGTERM
wait "$cover_pid"
set -e

# Make sure a coverage report has actually been generated. Else the
# publishing step will end up syncing an empty directory, which deletes
# the coverage report from doc.wikimedia.org.
test -f "$WORKSPACE"/cover/index.html

if [ -s "$LOG_DIR"/clover.xml ]; then
    # Since clover file is huge, compress it before archiving
    # We need to keep the original though for the cloverphp plugin
    gzip --best --keep "$LOG_DIR"/clover.xml

    clover-edit \
        "$LOG_DIR"/clover.xml \
        --name "MediaWiki core" \
        --remove-full-info \
        --save "$WORKSPACE"/cover/clover.xml

    # Publish a compressed form of the xml clover report
    gzip --best --stdout "$LOG_DIR"/clover.xml > "$WORKSPACE"/cover/clover.xml.gz
fi
