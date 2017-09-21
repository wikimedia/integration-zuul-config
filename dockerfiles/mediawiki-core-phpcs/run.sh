#!/usr/bin/env bash

LOG_DIR="$HOME/log"

cd /mediawiki
/srv/composer/vendor/bin/composer install
./vendor/bin/phpcs -p -s --report-full "--report-checkstyle=${LOG_DIR}/checkstyle.xml"
