#!/usr/bin/env bash

# This entry point is for repositories having node_modules commited under /src,
# typically the /deploy repositories for MediaWiki services.
#
# For example parsoid comes with two repositories:
#
# mediawiki/services/parsoid: the actual source code
# mediawiki/services/parsoid/deploy: node_modules and code under /src
#
# To fullfill tests dependencies, a script installs devDependencies one by one.
# The code dependencies are supposedly already commited in the repository
# src/node_modules.

umask 002

set -euxo pipefail

[ -d "/src/node_modules" ] || {
    echo "Failed to find node_modules directory!";
    exit 1;
}

node --version
npm --version

echo "Injecting dev dependencies from source repo into deploy node_modules"
cd /src
/npm-install-dev.py

# grunt.loadNpmTasks() does not honor NODE_PATH so fake it
# https://github.com/gruntjs/grunt-cli/pull/18
# https://phabricator.wikimedia.org/T92369
ln -fs /src/node_modules /src/src/node_modules

PATH="$PATH:/src/src/node_modules/.bin"
export PATH

cd /src/src
npm run-script "${@:-test}"
