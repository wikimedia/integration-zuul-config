#!/usr/bin/env bash

umask 002

set +x

/opt/sonar-scanner/bin/sonar-scanner -Dsonar.login=$SONAR_API_KEY "$@"
