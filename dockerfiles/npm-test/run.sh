#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src

node --version
npm --version

# Attempt to reste node_modules from the cache if any.
rsync \
    --archive \
    --ignore-missing-args \
    --delete-delay \
    "$XDG_CACHE_HOME"/node_modules /src
# Clean out packages that might no more be listed on the dependencies list
npm prune

npm install --no-progress

# Save node_modules to the cache
rsync \
    --archive \
    --ignore-missing-args \
    --delete-delay \
    /src/node_modules "$XDG_CACHE_HOME"

npm test
