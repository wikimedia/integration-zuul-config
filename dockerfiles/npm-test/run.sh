#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src

node --version
npm --version
npm install --no-progress --clean
npm test
