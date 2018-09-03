#!/usr/bin/env bash

set -euxo pipefail

umask 002

cd /mediawiki/$THING_SUBNAME

# Allow overriding version if explicitly specified
SECCHECK_VERSION=${SECCHECK_VERSION:-""}
if [ ! -z "$SECCHECK_VERSION" ]; then
    cat composer.json | jq --tab --arg version $SECCHECK_VERSION '. + {extra: {"phan-taint-check-plugin": $version}}' > tmpjsonfile.json
    mv tmpjsonfile.json composer.json
fi

if ! jq -e '.extra."phan-taint-check-plugin"' composer.json; then
    echo "phan-taint-check-plugin not configured"
    exit 0
fi

composer require --dev mediawiki/phan-taint-check-plugin $(jq -r '.extra."phan-taint-check-plugin"' composer.json)

SECCHECK_MODE=${SECCHECK_MODE:-seccheck-fast-mwext}

# Save the output as `seccheck-issues`
./vendor/bin/$SECCHECK_MODE $@ | tee /mediawiki/seccheck-issues
