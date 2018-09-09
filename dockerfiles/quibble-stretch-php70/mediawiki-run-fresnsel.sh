#!/bin/bash
#
# Create a Fresnel recording for the before and after state,
# and produce a comparison.
#
# Outputs: (TODO)

set -eux -o pipefail

export FRESNEL_DIR="$LOG_DIR/fresnel_records"

fresnel record "after"

echo 'todo: run "git checkout HEAD^" in the target zuul project directory (core, or extension)'

fresnel record "before"

fresnel compare "before" "after"
