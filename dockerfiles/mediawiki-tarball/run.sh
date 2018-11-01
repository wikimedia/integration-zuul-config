#!/usr/bin/env bash

umask 002

set -exo pipefail

cd /src
git pull

python3 -m virtualenv -p python3 venv
source venv/bin/activate
# TODO: Debianize so we're not trusting pypi
pip install git-archive-all==1.18.2

# Default to master if no branch set
ZUUL_BRANCH=${ZUUL_BRANCH:-"master"}

/opt/release/make-release/makerelease2.py /src $ZUUL_BRANCH --output-dir /dist
