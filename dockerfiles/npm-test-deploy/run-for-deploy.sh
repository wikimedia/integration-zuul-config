#!/bin/bash

set -euxo pipefail

umask 0002

node --version
npm --version

# All modules should already be in the deploy repo, no npm install we just
# install the development dependencies.
export NODE_PATH=/src/node_modules
export PATH="$PATH:/src/node_modules/.bin"

rm -f /src/src/node_modules
cd /src
/npm-install-dev.py

# grunt.loadNpmTasks() does not honor NODE_PATH so fake it
# https://github.com/gruntjs/grunt-cli/pull/18
# https://phabricator.wikimedia.org/T92369
ln -fs /src/node_modules /src/src/node_modules

cd /src/src
exec npm run-script "${@:-test}"
