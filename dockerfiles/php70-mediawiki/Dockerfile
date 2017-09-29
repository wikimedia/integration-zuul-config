FROM wmfreleng/php70:latest

USER root

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        # Needed for composer to install things from dist
        php7.0-zip \
        # Needed for mediawiki
        php-ast php7.0-mbstring php7.0-xml && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER nobody
