#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src

composer --ansi validate --no-check-publish
composer install --no-progress --prefer-dist
composer test
