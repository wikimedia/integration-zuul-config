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

Update Jenkins jobs which name starts with "selenium":

    $ jenkins-jobs --conf etc/jenkins_jobs.ini update config/jjb/ selenium*

## Running tests

To test the configuration, we use tox and you need at least version 1.9+ ([bug T125705](https://phabricator.wikimedia.org/T125705))
to run the test suite. Running `tox` in the main dir of your local clone runs the tests.

## Whitelist volunteer users

https://www.mediawiki.org/wiki/Continuous_integration/Whitelist
