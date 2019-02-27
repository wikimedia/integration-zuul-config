#!/bin/bash
#
# Asks Zuul server to validate its layout with the list of Jenkins jobs
# deployed. This is intended to be used before merge to ensure that all
# jobs referenced have been deployed.
#
# When run outside of a tox virtualenv, the script would install the
# zuul_tests environment and uses the zuul-server command it provides.
#

set -eu

_dir="$(dirname "$0")"
repodir="$(realpath "$_dir/..")"

if [ -z "${1:-}" ]; then
    echo "Usage: $(basename "$0") <layout file>"
    exit 1
fi

if [ ! -e "${1}" ]; then
    echo "Layout file not found: ${1}"
    exit 1
fi

# shellcheck source=/dev/null
source "$_dir"/setup-zuul-server.inc.sh

"$ZUUL_SERVER_BIN" --version
set -x
exec "$ZUUL_SERVER_BIN" \
    -c "$repodir"/tests/fixtures/zuul-dummy.conf \
    -t \
    -l "${1}"
