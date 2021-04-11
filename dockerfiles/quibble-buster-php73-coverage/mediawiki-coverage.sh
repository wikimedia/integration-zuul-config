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
if [[ ! -v CODEHEALTH ]]; then
  php -d extension=pcov.so -d pcov.enabled=1 -d pcov.directory=$MW_INSTALL_PATH/extensions -d pcov.exclude='@tests@' \
      tests/phpunit/phpunit.php \
          --exclude-group Dump,Broken,ParserFuzz,Stub \
          --coverage-clover "$LOG_DIR"/clover.xml \
          --coverage-html "$WORKSPACE/cover" &
else
  phpunit-suite-edit "$MW_INSTALL_PATH/phpunit.xml.dist"
  php -d extension=pcov.so -d pcov.enabled=1 -d pcov.directory=$MW_INSTALL_PATH/extensions -d pcov.exclude='@tests@' \
    vendor/bin/phpunit \
    --exclude-group Dump,Broken,ParserFuzz,Stub \
    --coverage-clover "$LOG_DIR"/clover.xml \
    --log-junit "$LOG_DIR"/junit.xml \
    tests/phpunit/unit &
fi
cover_pid=$!
relay_signals SIGINT SIGTERM
wait "$cover_pid"
set -e

# Make sure a coverage report has actually been generated. Else the
# publishing step will end up syncing an empty directory, which deletes
# the coverage report from doc.wikimedia.org.
# If we're not operating the in the codehealth pipeline context, check to see
# if the HTML coverage report was generated. If it was not, exit with a failure.
if [[ ! -v CODEHEALTH ]]; then
  test -f "$WORKSPACE"/cover/index.html
fi

# In codehealth pipeline context, make necessary modifications to junit.xml
if [[ -v CODEHEALTH ]] && [ -f "$LOG_DIR/junit.xml" ]; then
  phpunit-junit-edit "$LOG_DIR/junit.xml"
fi

if [ -s "$LOG_DIR"/clover.xml ] && [[ ! -v CODEHEALTH ]] ; then
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
