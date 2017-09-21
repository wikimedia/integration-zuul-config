FROM wmfreleng/composer:latest as composer

FROM wmfreleng/php-mediawiki:latest

USER root

COPY --from=composer /srv/composer /srv/composer

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        ca-certificates && \
    apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd -r phpcs && useradd --no-log-init -r -g phpcs phpcs

USER phpcs

COPY run.sh /run.sh

ENTRYPOINT /bin/bash /run.sh
