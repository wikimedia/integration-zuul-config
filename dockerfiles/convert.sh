#!/bin/bash
set -eu
dir=$1
pkg=$2
version="${3:-0.1.0}"
pushd "$dir"
dch --distribution wikimedia --force-distribution --package "${pkg}" 'Initial conversion to docker-pkg' -c changelog --create -v "${version}"
git mv Dockerfile Dockerfile.template
echo "Package: ${pkg}" > control
edit control
popd
