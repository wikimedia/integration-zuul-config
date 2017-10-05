FROM wmfreleng/php:latest

USER root

COPY .cache-buster-composer /.cache-buster-composer

RUN git clone --depth 1 https://gerrit.wikimedia.org/r/p/integration/composer.git /srv/composer && \
    rm -rf /srv/composer/.git
RUN ln -s /srv/composer/vendor/bin/composer /usr/bin/composer

USER nobody
ENTRYPOINT ["/srv/composer/vendor/bin/composer"]
CMD ["help"]
