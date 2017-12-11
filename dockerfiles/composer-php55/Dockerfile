FROM wmfreleng/composer:latest as composer

FROM wmfreleng/php55:latest

COPY --from=composer /srv/composer /srv/composer
COPY --from=composer /.cache-buster-composer /.cache-buster-composer
# Manually link since COPY copies symlink destination instead of the actual symlink
USER root
RUN ln -s /srv/composer/vendor/bin/composer /usr/bin/composer

USER nobody

# If a later dockerfile enables xdebug, don't
# spam warnings about it.
ENV COMPOSER_DISABLE_XDEBUG_WARN=1

ENTRYPOINT ["/srv/composer/vendor/bin/composer"]
CMD ["help"]
