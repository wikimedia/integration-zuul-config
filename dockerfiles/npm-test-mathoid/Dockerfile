FROM wmfreleng/npm-test

USER root
RUN apt-get update \
    && apt-get install --yes \
        librsvg2-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
USER nobody
