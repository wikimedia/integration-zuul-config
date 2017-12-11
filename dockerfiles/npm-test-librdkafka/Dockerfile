FROM wmfreleng/npm-test

USER root
RUN apt-get update \
    && apt-get install --yes \
        libsasl2-dev \
    && apt-get install --yes -t jessie-wikimedia \
        librdkafka-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
USER nobody
