#!/usr/bin/env bash
set -euxo pipefail

source /srv/emsdk/emsdk_env.sh

# TODO: move this to Gerrit?
git clone --depth=1 https://github.com/legoktm/demo -b patch-1 /srv/demo

cp -r /src /srv/demo/phan-taint-check-plugin
cd /srv/demo

./build.sh

cp -r html /src/html
