#!/bin/bash

git config --global user.email "you@example.com"
git config --global user.name "Your Name"

set -euxo pipefail

SRC_DIR="$HOME/core/extensions/undertest"
LOG_DIR="$HOME/log"

capture_logs() {
    # Save logs
    mv "${SRC_DIR}"/tests/phan/issues/latest "${LOG_DIR}/phan-issues" || /bin/true
}

trap capture_logs EXIT

mkdir $SRC_DIR
cd $SRC_DIR

# Prepare patch set from zuul merger
git remote add zuul "${ZUUL_URL}/${ZUUL_PROJECT}"
git pull --quiet zuul master
git fetch --quiet zuul "$ZUUL_REF"
git checkout --quiet FETCH_HEAD
#git submodule --quiet update --init --recursive

#TODO don't hardcode the extension / target.....
#git clone --depth 1 https://gerrit.wikimedia.org/r/p/mediawiki/extensions/ElectronPdfService.git ~/core/extensions/undertest
#cd ~/core/extensions/undertest

PHAN=/srv/phan/vendor/bin/phan ~/core/tests/phan/bin/phan ~/core/extensions/undertest -m checkstyle

