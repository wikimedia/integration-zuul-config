#!/usr/bin/env bash

set -euxo pipefail

/run-generic.sh "/mediawiki/$THING_SUBNAME" "$@"
