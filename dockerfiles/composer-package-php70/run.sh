#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src

if [ -n "${COMPOSER_GITHUB_OAUTHTOKEN}" ]; then
  composer config -g github-oauth.github.com "${COMPOSER_GITHUB_OAUTHTOKEN}"
fi
composer --ansi validate
composer install --no-progress --prefer-dist
exec composer test
