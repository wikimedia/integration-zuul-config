FROM wmfreleng/tox

USER root
RUN apt-get update && \
    apt-get install --yes \
        libldap2-dev \
        libsasl2-dev \
    && \
    rm -rf /var/lib/apt/lists/*

USER nobody
