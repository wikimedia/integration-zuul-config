#!/bin/bash

set -eu
set -o pipefail

umask 002

set +x

# run clean and install to compile
./mvnw -gs /settings.xml clean install

# run sonar analysis using maven and send extra args if not on master branch
if [[ $ZUUL_BRANCH = "master" ]]; then
  ./mvnw -gs /settings.xml sonar:sonar
else
  ./mvnw -gs /settings.xml sonar:sonar -Dsonar.branch.target="$ZUUL_BRANCH" -Dsonar.branch.name="$ZUUL_CHANGE-$ZUUL_PATCHSET"
fi
# Analysis is sent via a webhook from SonarQube to a web application (SonarQube Bot)
# and the bot will comment in gerrit with Verified +1 for success or comment only
# for failure.
