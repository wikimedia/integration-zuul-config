FROM wmfreleng/composer:latest as composer

FROM wmfreleng/php:latest

USER root

COPY --from=composer /srv/composer /srv/composer

USER nobody
COPY run.sh /run.sh
ENTRYPOINT /bin/bash /run.sh
