#!/bin/bash
#
# Create a Fresnel recording for the before and after state,
# and produce a comparison.
#
# Outputs: (TODO)

set -eux -o pipefail

export FRESNEL_DIR="$LOG_DIR/fresnel_records"

fresnel record "after"

git checkout HEAD~1

fresnel record "before"

fresnel compare "before" "after"
