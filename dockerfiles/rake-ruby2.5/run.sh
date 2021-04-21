#!/bin/bash

set -euxo pipefail

umask 002

/utils/ci-src-setup.sh

bundle install --clean --path "${XDG_CACHE_HOME}/bundle"
exec bundle exec rake "${@:-test}"
