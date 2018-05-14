#!/bin/bash
set -exo pipefail

cd /src
# Grab the latest code
git pull
# Initialize the slimerjs submodule
git submodule update --init
python3 -m virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
./run.py --start-xvfb --threads 1 --logdir /log --fast
# Clean up empty log files
find /log -empty -type f -delete
