#!/bin/bash

set -e
set -u
set -x
set -o pipefail


# Get rid of jenkins sudo
rm -fv /etc/sudoers.d/jenkins
