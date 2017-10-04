FROM wmfreleng/composer:latest as composer

FROM wmfreleng/php:latest

USER root

COPY --from=composer /srv/composer /srv/composer

RUN install -d /srv/phan -o nobody

ENV PHAN /srv/phan/vendor/bin/phan

USER nobody

RUN  cd /srv/phan && \
     /srv/composer/vendor/bin/composer require etsy/phan:0.8 && \
     rm -rf /cache/*

ENTRYPOINT ["/mediawiki/tests/phan/bin/phan"]
