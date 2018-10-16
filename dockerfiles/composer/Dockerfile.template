FROM {{ "php" | image_tag }}

USER root

RUN git clone --depth 1 https://gerrit.wikimedia.org/r/p/integration/composer.git /srv/composer \
    && rm -rf /srv/composer/.git \
    && ln -s /srv/composer/vendor/bin/composer /usr/bin/composer

# Script to 'composer require' solely dev dependencies. Copied to /srv/composer
# since child containers usually: COPY --from=composer /srv/composer /srv/composer
COPY composer-install-dev-only.bash /srv/composer/composer-install-dev-only
COPY security-check.sh /srv/composer/security-check

RUN {{ "jq curl" | apt_install }}

USER nobody

# If a later dockerfile enables xdebug, don't
# spam warnings about it.
ENV COMPOSER_DISABLE_XDEBUG_WARN=1

ENTRYPOINT ["/srv/composer/vendor/bin/composer"]
CMD ["help"]
