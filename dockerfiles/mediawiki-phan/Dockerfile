FROM wmfreleng/composer:latest as composer

FROM wmfreleng/php-mediawiki:latest

USER root

COPY --from=composer /srv/composer /srv/composer

RUN groupadd -r phan && \
    useradd --no-log-init --system --create-home -g phan phan && \
    install -d /srv/phan -o phan -g phan

ENV PHAN /srv/phan/vendor/bin/phan

USER phan

RUN  cd /srv/phan && \
     /srv/composer/vendor/bin/composer require etsy/phan:0.8 && \
     rm -rf ~/.composer

ENTRYPOINT ["/mediawiki/tests/phan/bin/phan"]
