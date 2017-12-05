#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src

node --version
npm --version

rsync \
    --archive \
    --delete-delay \
    "$XDG_CACHE_HOME"/node_modules/ /src/node_modules/
npm prune
npm install --no-progress

rsync \
    --archive \
    --delete-delay \
    /src/node_modules/ "$XDG_CACHE_HOME"/node_modules/
npm test
