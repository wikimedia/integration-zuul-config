#!/bin/bash

set -euxo pipefail

umask 002
LOG_DIR=/log
export LOG_DIR

MW_CORE='https://gerrit.wikimedia.org/r/mediawiki/core'

# Strip "refs/heads/wmf" from "$ZUUL_REF" so we're just left with just a
# version number like "1.33.0-wmf.18"
ZUUL_REF="${ZUUL_REF/refs\/heads\/wmf\/}"

# Get current sorted upstream mediawiki versions
mapfile -t VERSIONS < <(git ls-remote -h "$MW_CORE" | \
    awk '/wmf\// {gsub("refs/heads/wmf/", ""); print $2}' | \
    sort --version-sort --reverse)

if [[ "${VERSIONS[0]}" != "${ZUUL_REF}" ]]; then
    echo "${ZUUL_REF} is not the latest version, taking no action..."
    exit 1
fi

OLD_VERSION="${VERSIONS[1]}"
NEW_VERSION="${VERSIONS[0]}"

echo "Building Changelog for ${OLD_VERSION}..${NEW_VERSION}"

# Update the mediawiki/tools/release repo, envvar set by dockerfile
git -C "$TOOLS_RELEASE_DIR" pull --quiet origin master
git -C "$TOOLS_RELEASE_DIR" submodule --quiet update --init --recursive

# Actually make deploy notes
python3 /src/make-deploy-notes/makedeploynotes.py \
    "$OLD_VERSION" "$NEW_VERSION" > \
        "$LOG_DIR/deploy-notes-${NEW_VERSION}"

# Upload deploy notes
php /src/make-deploy-notes/jenkinsUploadChangelog.php \
    "$NEW_VERSION" \
    "$LOG_DIR/deploy-notes-${NEW_VERSION}"
