#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src

# If there's no lock file, then generate one
if [ ! -f "composer.lock" ]; then
    composer install --no-progress --prefer-dist
fi

curl -i -H "Accept: text/plain" https://security.sensiolabs.org/check_lock -F lock=@composer.lock -o sensiolabs.check
cat sensiolabs.check && grep -iF "X-Alerts: 0" sensiolabs.check
