FROM wmfreleng/composer:latest as composer

FROM wmfreleng/php-mediawiki:latest

USER root

COPY --from=composer /srv/composer /srv/composer

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        ca-certificates && \
    apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir -m 777 /log && mkdir -m 777 /src

USER nobody
COPY run.sh /run.sh
ENTRYPOINT /bin/bash /run.sh
