#!/bin/bash

set -euxo pipefail

umask 002

LOG_DIR=/log
export LOG_DIR

python3 /src/make-deploy-notes/makedeploynotes.py \
    "$OLD_VERSION" "$NEW_VERSION" > \
        "$LOG_DIR/deploy-notes-${NEW_VERSION}"

php /src/make-deploy-notes/jenkinsUploadChangelog.php \
    "$NEW_VERSION" \
    "$LOG_DIR/deploy-notes-${NEW_VERSION}"
