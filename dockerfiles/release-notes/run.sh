#!/bin/bash

set -euxo pipefail

umask 002
LOG_DIR=/log
export LOG_DIR

GIT='https://gerrit.wikimedia.org/r'
GITILES='https://gerrit.wikimedia.org/g'
MW_CORE="${GIT}/mediawiki/core"
BRANCH="${ZUUL_BRANCH##wmf/}"

# Check that there are commits on the branch that differ from master
COMMITS=$(curl -Ls "${GITILES}"'/mediawiki/core/+log/master..'"${ZUUL_BRANCH}"'?format=JSON&no-merges' | \
            tail -c+6 | \
            jq '.log[]')

if [ -z "$COMMITS" ]; then
    echo "No commits found for ${ZUUL_BRANCH}. Exiting..."
    exit 1
fi

# Get current sorted upstream mediawiki versions
mapfile -t VERSIONS < <(git ls-remote -h "$MW_CORE" | \
    awk '/wmf\// {gsub("refs/heads/wmf/", ""); print $2}' | \
    sort --version-sort --reverse)

if [[ "${VERSIONS[0]}" != "$BRANCH" ]]; then
    echo "${ZUUL_BRANCH} does not match the latest wmf branch (${VERSIONS[0]})"
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
