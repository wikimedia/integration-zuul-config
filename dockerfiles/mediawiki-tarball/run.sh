#!/usr/bin/env bash

umask 002

set -exo pipefail

cd /src
git pull

python3 -m virtualenv -p python3 venv
source venv/bin/activate
pip install git-archive-all==1.18.2

# Default to master if no branch set
ZUUL_BRANCH=${ZUUL_BRANCH:-"master"}

# FIXME does this use the git cache properly?
git clone https://gerrit.wikimedia.org/r/mediawiki/core
cd core && git submodule update --init
cd /src

mkdir dist
./make-release/makerelease2.py /src/core $ZUUL_BRANCH --output-dir dist

