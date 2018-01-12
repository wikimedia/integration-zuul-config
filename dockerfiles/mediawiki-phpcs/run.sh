#!/usr/bin/env bash

umask 002

cd /src

composer install --no-progress --prefer-dist
./vendor/bin/phpcs -p -s --report-full "--report-checkstyle=/log/checkstyle.xml"
