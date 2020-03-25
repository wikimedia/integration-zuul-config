#!/bin/sh
# Entrypoint for running composer.
# If COMPOSER_GITHUB_OAUTHTOKEN is set in the environment, that value will be
# installed as a token to pass to GitHub when fetching package contents.
if [ -n "${COMPOSER_GITHUB_OAUTHTOKEN}" ]; then
  /srv/composer/vendor/bin/composer config -g github-oauth.github.com "${COMPOSER_GITHUB_OAUTHTOKEN}"
fi
exec /srv/composer/vendor/bin/composer "$@"
