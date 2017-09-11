#!/bin/bash

# This is copied in Dockerfile to ensure that a build step grabs a fresh
# copy of the git repo when it is updated rather than using a layer from
# the local Docker cache.

git ls-remote https://gerrit.wikimedia.org/r/operations/puppet | \
   grep refs/heads/production | \
   cut -f 1 \
> .cache-buster