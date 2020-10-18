#!/bin/sh

# If we have explicitly enabled Xdebug, don't spam warnings about it
export COMPOSER_DISABLE_XDEBUG_WARN=1

# Entrypoint for running composer.
# If COMPOSER_GITHUB_OAUTHTOKEN is set in the environment, that value will be
# installed as a token to pass to GitHub when fetching package contents.
if [ -n "${COMPOSER_GITHUB_OAUTHTOKEN}" ]; then
  /usr/bin/composer config -g github-oauth.github.com "${COMPOSER_GITHUB_OAUTHTOKEN}"
fi
exec /usr/bin/composer "$@"
