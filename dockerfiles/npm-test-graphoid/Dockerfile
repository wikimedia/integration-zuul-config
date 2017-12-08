FROM wmfreleng/npm-test

USER root
RUN apt-get update \
    && apt-get install --yes \
        libcairo2-dev \
        libgif-dev \
        libpango1.0-dev \
        libjpeg62-turbo-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
USER nobody
