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

jobslist=$(mktemp --tmpdir zuul-layout-validate_jobslist.XXXX)
trap 'rm "$jobslist"' EXIT

echo "Getting list of jobs from Jenkins."
python "$repodir"/utils/jenkins-jobs-list.py > "$jobslist"
echo "There are $(wc -l "$jobslist"|cut -d\  -f1) jobs defined."

# shellcheck source=/dev/null
source "$_dir"/setup-zuul-server.inc.sh

"$ZUUL_SERVER_BIN" --version
exec "$ZUUL_SERVER_BIN" \
    -c "$repodir"/tests/fixtures/zuul-dummy.conf \
    -t "$jobslist" \
    -l "$repodir"/zuul/layout.yaml
