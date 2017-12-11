FROM wmfreleng/ci-jessie:latest

RUN echo "deb http://apt.wikimedia.org/wikimedia jessie-wikimedia component/ci" \
        > /etc/apt/sources.list.d/jessie-ci-php55.list && \
    apt-get update && \
    apt-get install --yes \
        php5.5-cli \
        php5.5-common \
        php5.5-curl \
        php5.5-dev \
        php5.5-gd \
        php5.5-gmp \
        php5.5-intl \
        php5.5-ldap \
        php5.5-luasandbox \
        php5.5-mbstring \
        php5.5-mcrypt \
        php5.5-mysql \
        php5.5-redis \
        php5.5-sqlite3 \
        php5.5-tidy \
        php5.5-xml \
        php5.5-xsl \
        php5.5-zip \
    && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER nobody

ENTRYPOINT ["php"]
CMD ["--help"]
