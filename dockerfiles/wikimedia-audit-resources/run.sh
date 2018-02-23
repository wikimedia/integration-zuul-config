#!/bin/bash
set -euxo pipefail

cd /src
# Grab the latest code
git pull
# Initialize the slimerjs submodule
git submodule update --init
./run.py --start-xvfb --threads 1 --logdir /logs
