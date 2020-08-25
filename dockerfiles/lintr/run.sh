#!/bin/bash

set -euxo pipefail

LOG_DIR="/log"
export LOG_DIR

/utils/ci-src-setup.sh

Rscript /lint.R | tee /log/lintr.log
