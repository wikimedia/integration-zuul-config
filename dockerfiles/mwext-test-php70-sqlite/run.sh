#!/usr/bin/env bash

set -euxo pipefail

umask 002

cd /src

# mw-set-env
MW_INSTALL_PATH=/src
# allow the dumping of corefiles, up to 64MB
# T142158
ulimit -c 2097152

export MW_INSTALL_PATH

export TMPDIR="/tmp"
export MW_TMPDIR="$TMPDIR"
export LOG_DIR="/log"

# mw-setup
# Ensure LocalSettings does not exist
rm -f "$MW_INSTALL_PATH/LocalSettings.php"

export MW_DB="jenkins_u${EXECUTOR_NUMBER}_mw"

# mw-install-sqlite
# Run MediaWiki installer
cd "$MW_INSTALL_PATH"
php maintenance/install.php \
	--confpath "$MW_INSTALL_PATH" \
	--dbtype=sqlite \
	--dbpath="$MW_TMPDIR" \
	--dbname="$MW_DB" \
	--pass testpass \
	TestWiki \
	WikiAdmin

# Installer creates files as 644 jenkins:jenkins
# Make the parent dir and files writable by Apache (bug 47639)
# - my_wiki.sqlite
# - wikicache.sqlite, wikicache.sqlite-shm, wikicache.sqlite-wal (since I864272af0)
chmod 777 $MW_TMPDIR/*

/srv/deployment/integration/slave-scripts/bin/mw-apply-settings.sh
/srv/deployment/integration/slave-scripts/bin/mw-run-update-script.sh
cd /src/extensions/$EXT_NAME
if [ -f composer.json ]; then
    composer --ansi validate --no-check-publish
    composer install --ansi --no-progress --prefer-dist --profile -v
    COMPOSER_PROCESS_TIMEOUT=600 composer --ansi test
    # Cleanup
    git clean -xqdf
fi
cd /src
/srv/deployment/integration/slave-scripts/bin/mw-fetch-composer-dev.sh
/srv/deployment/integration/slave-scripts/bin/mw-run-phpunit-allexts.sh
