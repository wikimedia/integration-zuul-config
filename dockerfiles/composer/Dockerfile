FROM wmfreleng/php:latest

USER root

COPY .cache-buster-composer /.cache-buster-composer

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        git \
        ca-certificates && \
    git clone --depth 1 https://gerrit.wikimedia.org/r/p/integration/composer.git /srv/composer && \
    rm -rf /srv/composer/.git && \
    apt-get remove --yes \
         git \
         ca-certificates && \
    apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd -r composer && useradd --no-log-init -r -g composer composer

USER composer

ENTRYPOINT ["/srv/composer/vendor/bin/composer"]
CMD ["help"]
