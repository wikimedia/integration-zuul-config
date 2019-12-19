#!/bin/bash

set -eu
set -o pipefail

umask 002

set +x

# # run sonar analysis using maven
./mvnw -gs /settings.xml sonar:sonar

# Analysis is sent via a webhook from SonarQube to a web application (SonarQube Bot)
# and the bot will comment in gerrit with Verified +1 for success or comment only
# for failure.
