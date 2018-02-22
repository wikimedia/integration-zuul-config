#!/bin/bash
set -eu -o pipefail

tox -e jenkins-jobs --notest

base_dir=$(realpath "$(dirname "$0")"/../)
JJB_BIN="$base_dir"/.tox/jenkins-jobs/bin/jenkins-jobs
CDIFF_BIN="$base_dir"/.tox/jenkins-jobs/bin/cdiff
JJB_CONF="$base_dir"/tests/fixtures/jjb-disable-query-plugins.conf
JJB_TEST="$JJB_BIN --conf $JJB_CONF -l warning test"

test_dir=$(mktemp -d --tmpdir jjbdiff.XXXX)
trap 'echo Deleting "$test_dir"; rm -R "$test_dir"' EXIT

mkdir -p "$test_dir"/{output-parent,output-proposed}

echo "Generating config for proposed patchset..."
$JJB_TEST "$base_dir"/jjb -o "$test_dir"/output-proposed

echo "Generating config for parent patchset..."
parent_config=$(mktemp -d --tmpdir)
git archive HEAD^ jjb|tar -C "$parent_config" -x
$JJB_TEST "$parent_config"/jjb -o "$test_dir"/output-parent

echo "--------------------------------------------"
echo " File changed"
echo "--------------------------------------------"
(diff --brief "$test_dir"/output-parent "$test_dir"/output-proposed || : ) | $CDIFF_BIN


echo "--------------------------------------------"
echo " Full diff"
echo "--------------------------------------------"
(diff --new-file -u "$test_dir"/output-parent "$test_dir"/output-proposed || : ) | $CDIFF_BIN
echo "Done."
