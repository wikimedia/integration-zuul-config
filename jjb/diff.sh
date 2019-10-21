#!/bin/bash
set -eu -o pipefail

tox -e jenkins-jobs --notest

base_dir=$(realpath "$(dirname "$0")"/../)

JJB_BIN=.tox/jenkins-jobs/bin/jenkins-jobs
DIFF_HIGHLIGHT_BIN="$base_dir"/.tox/jenkins-jobs/bin/diff-highlight
JJB_CONF=tests/fixtures/jjb-disable-query-plugins.conf
JJB_TEST="$JJB_BIN --conf $JJB_CONF -l warning test"

test_dir=$(mktemp -d --tmpdir jjbdiff.XXXX)
trap 'echo Deleting "$test_dir"; rm -R "$test_dir"' EXIT

mkdir -p "$test_dir"/{output-parent,output-proposed}

echo "Generating config for proposed patchset..."
(cd "$base_dir"
 $JJB_BIN --version
 $JJB_TEST ./jjb -o "$test_dir"/output-proposed)

echo "Generating config for parent patchset..."
parent_config=$(mktemp -d --tmpdir)
git archive HEAD^|tar -C "$parent_config" -x
(cd "$parent_config"
 tox -e jenkins-jobs --notest
 $JJB_BIN --version
 $JJB_TEST "$parent_config"/jjb -o "$test_dir"/output-parent
)

echo "--------------------------------------------"
echo " File changed"
echo "--------------------------------------------"
(diff --brief "$test_dir"/output-parent "$test_dir"/output-proposed || : ) | $DIFF_HIGHLIGHT_BIN


echo "--------------------------------------------"
echo " Full diff"
echo "--------------------------------------------"
(diff --new-file -u "$test_dir"/output-parent "$test_dir"/output-proposed || : ) | $DIFF_HIGHLIGHT_BIN
echo "Done."
