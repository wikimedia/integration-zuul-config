#!/bin/bash

set -eu
set -o pipefail

umask 002

set +x

# Initialize analysis, send data to SonarQube
/opt/sonar-scanner/bin/sonar-scanner -Dsonar.login="$SONAR_API_KEY" "$@"