#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src

if [ ! -f "package.json" ]; then
    echo "package.json not found, skipping\n"
    exit 0
fi

node --version
npm --version
rm -rf node_modules
npm install --no-progress
npm run-script "${@:-test}"
