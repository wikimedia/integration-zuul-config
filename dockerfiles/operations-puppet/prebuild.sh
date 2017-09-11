#!/bin/bash

set -eu
set -o pipefail

# This is copied in Dockerfile to ensure that a build step grabs a fresh
# copy of the git repo when it is updated rather than using a layer from
# the local Docker cache.

curl -s https://gerrit.wikimedia.org/r/projects/operations%2Fpuppet/branches/production | grep revision | xargs > .cache-buster