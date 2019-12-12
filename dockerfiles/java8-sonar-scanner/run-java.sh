#!/bin/bash

set -eu
set -o pipefail

umask 002

set +x

# # run sonar analysis using maven
./mvnw -gs /settings.xml sonar:sonar

# Wait a few seconds to give the analysis a chance to complete
sleep 5

poll-sonar-for-response target/sonar
