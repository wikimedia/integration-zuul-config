#!/usr/bin/env bash

cd /src
/srv/composer/vendor/bin/composer install
./vendor/bin/phpcs -p -s --report-full "--report-checkstyle=/log/checkstyle.xml"
