#!/bin/bash

set -eu
set -o pipefail

umask 002

set +x

if [[ ! -f /src/sonar-project.properties ]] && [[ ! -f /src/.sonar-project.properties ]]; then
    # Create directories if they don't already exist, so that sonar-scanner doesn't throw an error
    mkdir -p /src/resources /src/includes /src/src /src/modules /src/maintenance /src/tests
    touch /src/sonar-project.properties
    echo "sonar.sources=includes,src,modules,maintenance" >> /src/sonar-project.properties
    echo "sonar.test=tests" >> /src/sonar-project.properties
    # If test coverage exists, add this to the properties file.
    if [[ -f /src/coverage/lcov.info ]]; then
        echo "sonar.javascript.lcov.reportPaths=/src/coverage/lcov.info" >> /src/sonar-project.properties
    fi
    if [[ -f /workspace/log/coverage/junit.xml ]] && [[ -f /workspace/log/coverage/clover.xml ]]; then
        echo "sonar.php.tests.reportPath=/workspace/log/coverage/junit.xml" >> /src/sonar-project.properties
        echo "sonar.php.coverage.reportPaths=/workspace/log/coverage/clover.xml" >> /src/sonar-project.properties
    fi
fi
# Output sonar-project file to assist with debugging:
echo "== sonar-project.properties =="
cat /src/sonar-project.properties

# Initialize analysis, send data to SonarQube
/opt/sonar-scanner/bin/sonar-scanner -Dsonar.login="$SONAR_API_KEY" "$@"

# Poll for analysis completion.
echo "Checking for analysis completion"
ATTEMPT_COUNTER=0
MAX_ATTEMPTS=10

# For convenience, export the variables for the analysis task ID and the dashboard URL
export $( cat /src/.scannerwork/report-task.txt | grep ceTaskId )
export $( cat /src/.scannerwork/report-task.txt | grep dashboardUrl )
SONARQUBE_ANALYSIS_URL=https://sonarcloud.io/api/ce/task?id=$ceTaskId
SONARQUBE_ANALYSIS_RESPONSE=$( curl -s -u ${SONAR_API_KEY}: ${SONARQUBE_ANALYSIS_URL} | jq -r .[].status )

echo "Polling ${SONARQUBE_ANALYSIS_URL}"

until ( [[ ${SONARQUBE_ANALYSIS_RESPONSE} == "SUCCESS" ]] ); do
    if [[ ${ATTEMPT_COUNTER} -eq ${MAX_ATTEMPTS} ]];then
      echo "Max attempts reached"
      echo "Last analysis response: ${SONARQUBE_RAW_ANALYSIS_RESPONSE}"
      exit 1
    fi

    SONARQUBE_RAW_ANALYSIS_RESPONSE=$(curl -s -u ${SONAR_API_KEY}: ${SONARQUBE_ANALYSIS_URL} )
    SONARQUBE_ANALYSIS_RESPONSE=$( echo ${SONARQUBE_RAW_ANALYSIS_RESPONSE} | jq -r .[].status )
    printf '.'
    ATTEMPT_COUNTER=$(($ATTEMPT_COUNTER+1))
    sleep 15
done

ANALYSIS_ID=$( curl -s -u ${SONAR_API_KEY}: ${SONARQUBE_ANALYSIS_URL} | jq -r .[].analysisId )
QUALITY_GATE=$( curl -s -u ${SONAR_API_KEY}: https://sonarcloud.io/api/qualitygates/project_status?analysisId=${ANALYSIS_ID})

# Pretty-printed JSON output fo the quality gate. Better than nothing!
echo "== QUALITY GATE =="
echo ${QUALITY_GATE} | jq
QUALITY_GATE_STATUS=$(echo ${QUALITY_GATE} | jq -r .projectStatus.status)
echo "=========================="
echo "Quality gate status: ${QUALITY_GATE_STATUS}"
echo "Report URL: $dashboardUrl"
echo "=========================="
if [[ ${QUALITY_GATE_STATUS} == "ERROR" ]]; then
    exit 1;
fi
exit 0;
