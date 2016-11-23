#!/bin/bash
set -eu -o pipefail

jenkins-jobs update --delete-old jjb/

