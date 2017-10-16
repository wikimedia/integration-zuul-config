FROM wmfreleng/composer:latest

USER root

RUN install -d /srv/phan -o nobody

ENV PHAN /srv/phan/vendor/bin/phan

USER nobody

RUN  cd /srv/phan && \
     composer require etsy/phan:0.8 && \
     rm -rf /cache/*

COPY run.sh /run.sh
ENTRYPOINT ["/bin/bash", "/run.sh"]
