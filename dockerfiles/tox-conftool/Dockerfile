FROM wmfreleng/tox

USER root
RUN apt-get update && \
    apt-get install --yes \
        etcd \
    && \
    rm -rf /var/lib/apt/lists/*

USER nobody
