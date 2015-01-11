TESTING GRRIT-WM

# Wikimedia configuration for Jenkins

This repository holds the configuration of the Wikimedia Foundation Inc. Jenkins
jobs. It is meant to be used with a python script written by the OpenStack
Foundation: Jenkins Job Builder.

When you tweak or add jobs, follow the documentation maintained on mediawiki.org:

  https://www.mediawiki.org/wiki/CI/JJB

For more about the Jenkins Job Builder software and how to use it, refer to the upstream documentation:

  http://ci.openstack.org/jenkins-job-builder/

## Example Usage

Generate XML files for Jenkins jobs from YAML files:

    $ jenkins-jobs test config/jjb/ -o output/

Update Jenkins jobs which name starts with "browsertests":

    $ jenkins-jobs --conf etc/jenkins_jobs.ini update config/jjb/ browsertests*
