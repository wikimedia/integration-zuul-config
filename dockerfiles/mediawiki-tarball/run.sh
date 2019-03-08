#!/usr/bin/env bash

umask 002

set -exo pipefail

cd /opt/release
# Pull in any new changes since image rebuild
git pull
cd /src

. /opt/release/venv/bin/activate

cd /opt/release-driver
# Default to master if no branch set
make tarball releaseVer=${ZUUL_BRANCH:-"master"}
