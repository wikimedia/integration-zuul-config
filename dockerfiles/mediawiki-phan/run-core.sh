#!/usr/bin/env bash

set -euxo pipefail

umask 002

cd /mediawiki/

if [ ! -f .phan/config.php ]; then
    echo "Phan config not found"
    exit 0
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
        # New mediawiki-phan-config, phan is already required
    fi
fi

# Bypass expensive Symfony\Component\Console\Terminal::getWidth() (T219114#5084302)
export COLUMNS=80

export PHP_ARGS='-dextension=ast_101.so'
if [ -z "$PHAN_VERSION" ]; then
    install_phan
fi
exec /srv/phan/vendor/bin/phan -d . -p "$@"
