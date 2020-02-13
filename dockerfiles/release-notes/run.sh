#!/bin/bash

set -euxo pipefail

umask 002
LOG_DIR=/log
export LOG_DIR

MW_CORE='https://gerrit.wikimedia.org/r/mediawiki/core'

# Outputs the version value assigned to $wgVersion
parse_version() {
    read -r pattern <<-end
s/.*["']\([^"']*\)['"];$/\1/
end
    sed "$pattern"
}

# Shows commit/diff for includes/DefaultSettings.php
settings_diff() {
    git -C /src diff HEAD~ HEAD -- includes/DefaultSettings.php
}

# Check whether wgVersion has changed in DefaultSettings.php
if ! settings_diff | grep -qm 1 '^-\$wgVersion ='; then
    echo "wgVersion hasn't changed"
    echo "taking no action..."
    exit 1
fi

# Parse old and new values of wgVersion
OLD_WG_VERSION="$(settings_diff | grep -m 1 '^-\$wgVersion =' | cut -c 2- | parse_version)"
NEW_WG_VERSION="$(settings_diff | grep -m 1 '^+\$wgVersion =' | cut -c 2- | parse_version)"

if [[ "${OLD_WG_VERSION##*-}" != "alpha" ]]; then
    echo "wgVersion has changed from ${OLD_WG_VERSION} which is not an -alpha version"
    echo "taking no action..."
    exit 1
fi

# Get current sorted upstream mediawiki versions
mapfile -t VERSIONS < <(git ls-remote -h "$MW_CORE" | \
    awk '/wmf\// {gsub("refs/heads/wmf/", ""); print $2}' | \
    sort --version-sort --reverse)

if [[ "${VERSIONS[0]}" != "${NEW_WG_VERSION}" ]]; then
    echo "${NEW_WG_VERSION} does not match the latest wmf branch (${VERSIONS[0]})"
    echo "taking no action..."
    exit 1
fi

OLD_VERSION="${VERSIONS[1]}"
NEW_VERSION="${VERSIONS[0]}"

echo "Building Changelog for ${OLD_VERSION}..${NEW_VERSION}"

# Update the mediawiki/tools/release repo, envvar set by dockerfile
git -C "$RELEASE_TOOLS_DIR" pull --quiet origin master
git -C "$RELEASE_TOOLS_DIR" submodule --quiet update --init --recursive

# Actually make deploy notes
python3 "$RELEASE_TOOLS_DIR"/make-deploy-notes/makedeploynotes.py \
    "$OLD_VERSION" "$NEW_VERSION" > \
        "$LOG_DIR/deploy-notes-${NEW_VERSION}"

# Upload deploy notes
php "$RELEASE_TOOLS_DIR"/make-deploy-notes/jenkinsUploadChangelog.php \
    "$NEW_VERSION" \
    "$LOG_DIR/deploy-notes-${NEW_VERSION}"
