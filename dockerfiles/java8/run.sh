#!/bin/bash

set -euxo pipefail

umask 002

/utils/ci-src-setup.sh

exec /usr/local/bin/mvn "${@}"
