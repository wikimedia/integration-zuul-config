FROM wmfreleng/composer:latest

USER root

RUN install -d /srv/phan -o nobody

ENV PHAN /srv/phan/vendor/bin/phan

RUN echo "umask 0002" >> /etc/bash.bashrc

USER nobody

RUN  cd /srv/phan && \
     composer require etsy/phan:0.8 && \
     rm -rf /cache/*

ENTRYPOINT ["/mediawiki/tests/phan/bin/phan"]
