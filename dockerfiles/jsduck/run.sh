#!/usr/bin/env bash

umask 002

set -euxo pipefail

cd /src
jsduck --version
npm run doc
