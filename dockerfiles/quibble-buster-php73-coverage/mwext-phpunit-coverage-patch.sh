#!/bin/bash
#
# Verify coverage has improve for a MediaWiki extension patch
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
# - Coverage check reports in $LOG_DIR/coverage.html

set -eux -o pipefail

EXT_NAME=$(basename "$ZUUL_PROJECT")
cd "$MW_INSTALL_PATH/extensions/$EXT_NAME"

# Edit suite.xml to use the proper coverage paths
phpunit-suite-edit "$MW_INSTALL_PATH/tests/phpunit/suite.xml" --cover-extension "$EXT_NAME"

exec phpunit-patch-coverage check \
    --command "php -d extension=pcov.so -d pcov.enabled=1 -d pcov.directory=$PWD -d pcov.exclude='@(tests|vendor)@' -d pcov.initial.files=3000 \"\$MW_INSTALL_PATH\"/tests/phpunit/phpunit.php" \
    --html "$LOG_DIR"/coverage.html
