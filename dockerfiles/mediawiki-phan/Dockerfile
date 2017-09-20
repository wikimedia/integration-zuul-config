FROM wmfreleng/composer:latest as composer

FROM wmfreleng/php-mediawiki:latest

USER root

COPY --from=composer /srv/composer /srv/composer

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        ca-certificates && \
    apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/* && \
        mkdir /srv/phan && \
        cd /srv/phan && \
        /srv/composer/vendor/bin/composer require etsy/phan:0.8 && \
        rm -rf ~/.composer

RUN groupadd -r phan && useradd --no-log-init -r -g phan phan

ENV PHAN /srv/phan/vendor/bin/phan

USER phan

ENTRYPOINT ["/mediawiki/tests/phan/bin/phan"]