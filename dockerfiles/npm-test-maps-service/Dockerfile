FROM wmfreleng/npm-test

USER root
RUN apt-get update \
    && apt-get install --yes \
        libcairo2-dev \
        libgif-dev \
        libpango1.0-dev \
        libjpeg62-turbo-dev \
        fonts-dejavu \
        libboost-filesystem-dev \
        libboost-program-options-dev \
        libboost-regex-dev \
        libboost-system-dev \
        libboost-thread-dev \
        libgdal-dev \
        libicu-dev \
        libpq-dev \
        libcurl4-gnutls-dev \
        libproj-dev \
        libtiff-dev \
        libwebp5 \
        libmapbox-variant-dev \
        libmapnik-dev \
        mapnik-utils \
    && apt-get install --yes -t jessie-wikimedia \
        librdkafka-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
USER nobody
