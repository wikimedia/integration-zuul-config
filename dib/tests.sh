#!/bin/bash
# Wrapper to lint dib elements. Used by tox -edib

set -eux

cd `dirname $0`
dib-lint

# Commented out, would consume too much diskspace for now
#DIB_DEBIAN_USE_DEBOOTSTRAP_CACHE=1 ./build_image.sh
