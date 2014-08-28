# jenkins-job-builder-config

YAML files for Jenkins jobs at https://wmf.ci.cloudbees.com/

## Usage

Generate XML files for Jenkins jobs from YAML files:

    jenkins-jobs test config/ -o output/

Update Jenkins jobs:

    jenkins-jobs --conf etc/jenkins_jobs.ini update config/
