#!/usr/bin/env bash

umask 002

set -exo pipefail

cd /opt/release
# Pull in any new changes since image rebuild
git pull
cd /src
# Clean up any composer stuffs
git clean -ffdx
git submodule update --init

python3 -m virtualenv -p python3 venv
source venv/bin/activate
# TODO: Debianize so we're not trusting pypi
pip install git-archive-all==1.18.2 requests

# Default to master if no branch set
ZUUL_BRANCH=${ZUUL_BRANCH:-"master"}

/opt/release/make-release/makerelease2.py --output-dir /dist /src $ZUUL_BRANCH
