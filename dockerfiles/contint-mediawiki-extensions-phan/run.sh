#!/bin/bash

git config --global user.email "addshorewiki@gmail.com"
git config --global user.name "addshore"

set -euxo pipefail

HOME_DIR="/var/lib/jenkins"
EXT_DIR="${HOME_DIR}/mediawiki/extensions"
SRC_DIR="${EXT_DIR}/undertest"
LOG_DIR="${HOME_DIR}/log"

capture_logs() {
    cp "${SRC_DIR}/tests/phan/issues/latest" "${LOG_DIR}/phan-issues" || /bin/true
}

trap capture_logs EXIT

mkdir -p $LOG_DIR
mkdir $SRC_DIR

echo -e $EXT_DEPENDENCIES >> deps.txt
while read DEP
do
    DEP_DIR="${HOME_DIR}/${DEP}"
    mkdir -p $DEP_DIR
    cd $DEP_DIR
    git init
    git remote add zuul "${ZUUL_URL}/${DEP}"
    git pull --quiet zuul master
    git checkout --quiet master
    git submodule --quiet update --init --recursive
done < deps.txt

# TODO use zuul cloner instead of doing all this crap?

# Prepare patch set from zuul merger
cd $SRC_DIR
git init
git remote add zuul "${ZUUL_URL}/${ZUUL_PROJECT}"
git pull --quiet zuul master
git fetch --quiet zuul "$ZUUL_REF"
git checkout --quiet FETCH_HEAD
git submodule --quiet update --init --recursive

PHAN=/srv/phan/vendor/bin/phan ${HOME_DIR}/mediawiki/tests/phan/bin/phan ${SRC_DIR} -m checkstyle
