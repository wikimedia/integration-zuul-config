#!/bin/bash

set -eu
set -o pipefail

umask 002

set +x

# run clean and install to compile
mvn clean install

# run sonar analysis using maven and send extra args for sonar bot
mvn sonar:sonar -Dsonar.analysis.allowCommentOnMaster="1" -Dsonar.analysis.gerritProjectName="$ZUUL_PROJECT" -Dsonar.branch.target="$ZUUL_BRANCH" -Dsonar.branch.name="$ZUUL_CHANGE-$ZUUL_PATCHSET"

# Analysis is sent via a webhook from SonarQube to a web application (SonarQube Bot)
# and the bot will comment in gerrit with Verified +1 for success or comment only
# for failure.
