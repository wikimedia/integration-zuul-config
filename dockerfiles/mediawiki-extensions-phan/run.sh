#!/bin/bash
# TODO what is the deal with Depends-On: tags?

git config --global user.email "noone@wikimedia.org"
git config --global user.name "noone"

set -euxo pipefail

HOME_DIR="/var/lib/jenkins"
MW_DIR="${HOME_DIR}/mediawiki"
EXT_DIR="${MW_DIR}/extensions"
SRC_DIR="${EXT_DIR}/undertest"
LOG_DIR="${HOME_DIR}/log"

capture_logs() {
    cp "${SRC_DIR}/tests/phan/issues/latest" "${LOG_DIR}/phan-issues" || /bin/true
}

trap capture_logs EXIT

mkdir -p $LOG_DIR
mkdir $SRC_DIR

# Update to latest mediawiki core and vendor
cd $MW_DIR
git fetch --depth 1 "$ZUUL_URL/mediawiki/core" master
git checkout FETCH_HEAD
cd $MW_DIR/vendor
git fetch --depth 1 "$ZUUL_URL/mediawiki/vendor" master
git checkout FETCH_HEAD
cd $MW_DIR

echo -e $EXT_DEPENDENCIES >> deps.txt
while read DEP
do
    DEP_DIR="${HOME_DIR}/${DEP}"
    mkdir -p $DEP_DIR
    cd $DEP_DIR
    git init
    git fetch --depth 1 "${ZUUL_URL}/${DEP}" master
    git checkout FETCH_HEAD
    git submodule --quiet update --init --recursive
done < deps.txt

# TODO use zuul cloner instead of doing all this crap?

# Prepare patch set from zuul merger
cd $SRC_DIR
git init
git fetch --depth 1 --quiet "${ZUUL_URL}/${ZUUL_PROJECT}" "$ZUUL_REF"
git checkout --quiet FETCH_HEAD
git submodule --quiet update --init --recursive

PHAN=/srv/phan/vendor/bin/phan ${HOME_DIR}/mediawiki/tests/phan/bin/phan ${SRC_DIR} -m checkstyle