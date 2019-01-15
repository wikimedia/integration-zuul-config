#!/bin/bash

set -eu
set -o pipefail

test "${MEDIAWIKI_ENVIRONMENT:?MEDIAWIKI_ENVIRONMENT must be set}"

if [[ "$MEDIAWIKI_ENVIRONMENT" == "beta"* ]]; then
	echo MEDIAWIKI_PASSWORD="\$selenium_user_beta"
    test "${selenium_user_beta:?}"
	set +x
	export MEDIAWIKI_PASSWORD="$selenium_user_beta"
elif [ "$MEDIAWIKI_ENVIRONMENT" = "mediawiki" ] || [ "$MEDIAWIKI_ENVIRONMENT" = "test" ]; then
	echo MEDIAWIKI_PASSWORD="\$selenium_user_production"
    test "${selenium_user_production:?}"
	set +x
	export MEDIAWIKI_PASSWORD="$selenium_user_production"
else
	echo "MEDIAWIKI_ENVIRONMENT $MEDIAWIKI_ENVIRONMENT not supported!"
	exit 1
fi

export LOG_DIR="${LOG_DIR:-/log}"

# screenshots
export SCREENSHOT_FAILURES=true
export SCREENSHOT_FAILURES_PATH="$LOG_DIR"

# videos
export HEADLESS=true
#export HEADLESS_DISPLAY=$((70 + EXECUTOR_NUMBER % 20))
export HEADLESS_DESTROY_AT_EXIT=true
export HEADLESS_CAPTURE_PATH="$LOG_DIR"

echo "Will capture screenshots to $LOG_DIR. Set \$LOG_DIR to override."
exec /run.sh selenium
