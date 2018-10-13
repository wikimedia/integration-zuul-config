#!/usr/bin/env bash

set -euxo pipefail

umask 002

/mediawiki/tests/phan/bin/phan $@
