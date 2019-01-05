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

if [ -e 'npm-shrinkwrap.json' ] || [ -e 'package-lock.json' ]; then
    npm ci
else
    # Use whatever version matched in package.json devDependencies
    echo 'No package-lock.json or npm-shrinkwrap.json detected, doing full install'
    rm -rf node_modules
    npm install --no-progress
fi

npm run-script "${@:-test}"
