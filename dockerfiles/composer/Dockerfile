FROM wmfreleng/php:latest

USER root

COPY .cache-buster-composer /.cache-buster-composer

RUN git clone --depth 1 https://gerrit.wikimedia.org/r/p/integration/composer.git /srv/composer && \
    rm -rf /srv/composer/.git
RUN ln -s /srv/composer/vendor/bin/composer /usr/bin/composer

USER nobody

# If a later dockerfile enables xdebug, don't
# spam warnings about it.
ENV COMPOSER_DISABLE_XDEBUG_WARN=1

ENTRYPOINT ["/srv/composer/vendor/bin/composer"]
CMD ["help"]
