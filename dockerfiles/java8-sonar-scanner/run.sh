#!/bin/bash

set -eu
set -o pipefail

umask 002

set +x

if [ ! -f /src/sonar-project.properties ] && [ ! -f /src/.sonar-project.properties ]; then
    # Create directories if they don't already exist, so that sonar-scanner doesn't throw an error
    mkdir -p /src/resources /src/includes /src/src /src/modules /src/maintenance /src/tests
    touch /src/sonar-project.properties
    echo "sonar.sources=includes,src,modules,maintenance" >> /src/sonar-project.properties
    echo "sonar.test=tests" >> /src/sonar-project.properties
    # If test coverage exists, add this to the properties file.
    if [ -f /log/coverage/lcov.info ]; then
        echo "sonar.javascript.lcov.reportPaths=/log/coverage/lcov.info" >> /src/sonar-project.properties
    fi
    if [ -f /log/coverage/junit.xml ] && [ -f /log/coverage/clover.xml ]; then
        echo "sonar.php.tests.reportPath=/log/coverage/junit.xml" >> /src/sonar-project.properties
        echo "sonar.php.coverage.reportPaths=/log/coverage/clover.xml" >> /src/sonar-project.properties
    fi
fi

exec /opt/sonar-scanner/bin/sonar-scanner -Dsonar.login="$SONAR_API_KEY" "$@"
