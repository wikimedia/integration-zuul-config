#!/usr/bin/env bash

umask 002

set -exo pipefail

cd /opt/release
# Pull in any new changes since image rebuild
git pull

cd /opt/release-driver
# Default to master if no branch set
make ${TARGET:-"tarball"} workDir=/src releaseVer=${RELEASE_VERSION:-""} rebuildOkay=${REBUILD_OK:-"false"}
