#!/usr/bin/env bash

set -euxo pipefail

umask 002

if [ ! -f "/mediawiki/$THING_SUBNAME/tests/phan/config.php" ]; then
    echo "Phan config not found\n"
    exit 0
fi

/mediawiki/tests/phan/bin/phan $@
