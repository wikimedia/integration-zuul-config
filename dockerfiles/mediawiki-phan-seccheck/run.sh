#!/usr/bin/env bash

set -euxo pipefail

umask 002

cd /mediawiki/extensions/$EXT_NAME
composer require --dev mediawiki/phan-taint-check-plugin 1.1.0

SECCHECK_MODE=${SECCHECK_MODE:-seccheck-fast-mwext}

# Save the output as `seccheck-issues`
./vendor/bin/$SECCHECK_MODE $@ | tee /mediawiki/seccheck-issues
