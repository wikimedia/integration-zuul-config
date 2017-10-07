#!/usr/bin/env bash

set -euxo pipefail

cd /src

node --version
npm --version
rm -rf node_modules
npm install
npm test
