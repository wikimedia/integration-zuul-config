#!/bin/bash

set -eu
set -o pipefail

LOG_DIR=${LOG_DIR:-/log}

if [ ! -d /src/wikimedia/fundraising/crm ]; then
    echo "Civi CRM not found at /src/wikimedia/fundraising/crm"
    echo "You must first clone the git repositories and volume mount"
    echo "them to /src."
    exit 1
fi

set -x
/src/wikimedia/fundraising/crm/bin/ci-create-dbs.sh
/src/wikimedia/fundraising/crm/bin/ci-populate-dbs.sh
cd /src/wikimedia/fundraising/crm

export PATH=$PATH:/src/wikimedia/fundraising/crm/civicrm-buildkit/bin
/src/wikimedia/fundraising/crm/vendor/bin/phpunit --log-junit "${LOG_DIR}/junit-phpunit.xml"
