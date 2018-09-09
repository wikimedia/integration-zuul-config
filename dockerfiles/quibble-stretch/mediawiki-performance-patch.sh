#!/bin/bash
#
# ..

set -eux -o pipefail

# Let mediawiki-$nametbd test against $MW_SERVER,
# and write results to the given path.
$nametbd --record "$LOG_DIR/after.json"

echo 'todo: run "git checkout HEAD^" in the target zuul project directory (core, or extension)'

# Test again, then compare the results,
# and print nice comparisons to standard out.
$nametbd --record "$LOG_DIR/before.json" --compare "$LOG_DIR/after.json"
