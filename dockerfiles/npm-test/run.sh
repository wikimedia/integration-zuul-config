#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src

node --version
npm --version
npm prune
npm install --no-progress
npm test
