#!/usr/bin/env bash

set -euxo pipefail

cd /src

composer --ansi validate
composer install --no-progress --prefer-dist
composer test
