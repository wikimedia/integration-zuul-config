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

SECCHECK_VERSION=$(jq -r '.extra."phan-taint-check-plugin"' composer.json)

# Install into /opt/phan so we don't conflict with any extension dependencies
cd /opt/phan/
composer require mediawiki/phan-taint-check-plugin $SECCHECK_VERSION

SECCHECK_MODE=${SECCHECK_MODE:-seccheck-fast-mwext}
export SECURITY_CHECK_EXT_PATH=/mediawiki/$THING_SUBNAME
export MW_INSTALL_PATH=/mediawiki/

# Save the output as `seccheck-issues`
./vendor/bin/$SECCHECK_MODE $@ | tee /mediawiki/seccheck-issues
