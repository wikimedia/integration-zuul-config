#!/usr/bin/env bash

set -euxo pipefail

umask 002

cd "/mediawiki/$THING_SUBNAME"

if [ ! -f "/mediawiki/$THING_SUBNAME/.phan/config.php" ]; then
    # Look in old location
    if [ ! -f "/mediawiki/$THING_SUBNAME/tests/phan/config.php" ]; then
        echo "Phan config not found"
        exit 0
    fi
fi

function install_phan {
    # Subshell so we don't mess with path
    (cd /srv/phan && composer require "phan/phan:$PHAN_VERSION")
}

# First look for phan version in root composer.json
if jq -e '.extra."phan"' composer.json; then
    PHAN_VERSION=$(jq -r '.extra."phan"' composer.json)
else
    # Then look for it via mediawiki-phan-config
    CFG_COMPOSER="vendor/mediawiki/mediawiki-phan-config/composer.json"
    if jq -e '.extra."phan"' $CFG_COMPOSER; then
        PHAN_VERSION=$(jq -r '.extra."phan"' $CFG_COMPOSER)
    else
        # Old-style, fallback to 0.8
        PHAN_VERSION="0.8"
    fi
fi

if [ -f .phan/config.php ]; then
    # new-style phan, using modern paths and newer ast
    export PHP_ARGS='-dextension=ast_101.so'
    install_phan
    exec /srv/phan/vendor/bin/phan -d . -p "$@"
else
    # old-style, using tests/phan and the wrapper shipped with mediawiki/core
    export PHP_ARGS='-dextension=ast_012.so'
    install_phan
    # Inject the extension repository as the first argument to trigger custom
    # logic in the wrapper. T219114#5176487
    exec /mediawiki/tests/phan/bin/phan "/mediawiki/$THING_SUBNAME" "$@"
fi
