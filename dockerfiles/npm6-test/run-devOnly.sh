#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src

node --version
npm --version

if [ -e 'npm-shrinkwrap.json' ] || [ -e 'package-lock.json' ]; then
    npm ci --only=dev
else
    # Use whatever version matched in package.json devDependencies
    echo 'No package-lock.json or npm-shrinkwrap.json detected, doing full install'
	rm -rf node_modules
	npm install --no-save --only=dev --no-progress
fi

npm run-script "${@:-test}"
