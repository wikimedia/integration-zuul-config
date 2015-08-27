#!/bin/sh
# Wrapper to lint dib elements. Used by tox -edib

set -eux

cd `dirname $0`
dib-lint
./build_image.py
