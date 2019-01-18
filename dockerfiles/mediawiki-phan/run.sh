#!/usr/bin/env bash

set -euxo pipefail

umask 002

cd /mediawiki/$THING_SUBNAME

if [ ! -f "/mediawiki/$THING_SUBNAME/.phan/config.php" ]; then
    # Look in old location
    if [ ! -f "/mediawiki/$THING_SUBNAME/tests/phan/config.php" ]; then
        echo "Phan config not found\n"
        exit 0
    fi
fi

function install_phan {
    # Subshell so we don't mess with path
    (cd /srv/phan && composer require phan/phan:$PHAN_VERSION)
}

if jq -e '.extra."phan"' composer.json; then
    # new-style phan, using modern paths and newer ast
    PHAN_VERSION=$(jq -r '.extra."phan"' composer.json)
    export PHP_ARGS='-dextension=ast_017.so'
    install_phan
    /srv/phan/vendor/bin/phan -d . -p
else
    # old-style, using tests/phan and MW wrapper
    PHAN_VERSION="0.8"
    export PHP_ARGS='-dextension=ast_012.so'
    install_phan
    /mediawiki/tests/phan/bin/phan $@
fi

