#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src

node --version
npm --version
rm -rf node_modules
npm install --no-progress
npm run-script "${@:-test}"
