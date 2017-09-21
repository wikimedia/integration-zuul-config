#!/usr/bin/env bash

cd /mediawiki
composer install
mkdir -p log
./vendor/bin/phpcs -p -s --report-full --report-checkstyle=./log/checkstyle.xml
