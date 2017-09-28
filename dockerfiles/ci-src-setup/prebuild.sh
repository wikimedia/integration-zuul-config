#!/bin/bash

set -e

# This is copied in Dockerfile to ensure that a build step grabs a fresh
# copy of the git repo when it is updated rather than using a layer from
# the local Docker cache.

git ls-remote --exit-code https://gerrit.wikimedia.org/r/p/integration/jenkins.git refs/heads/master > .cache-buster-integration-jenkins
