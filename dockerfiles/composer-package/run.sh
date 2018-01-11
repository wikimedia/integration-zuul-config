#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src

composer --ansi validate
composer install --no-progress --prefer-dist
exec composer test
