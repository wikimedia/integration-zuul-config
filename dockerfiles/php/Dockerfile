FROM wmfreleng/ci-stretch:latest

RUN apt-get update && \
    apt-get install --yes \
        php7.0-cli \
        # Needed for composer to install things from dist
        php7.0-zip \
        # Needed by libraries/MediaWiki
        php-ast php7.0-curl php7.0-dba php7.0-mbstring php-redis php7.0-sqlite3 php-xdebug php7.0-xml && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Disable xdebug by default due to its performance impact
RUN phpdismod xdebug

USER nobody

ENTRYPOINT ["php"]
CMD ["--help"]
