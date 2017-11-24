FROM wmfreleng/tox

USER root
RUN apt-get update && \
    apt-get install --yes \
        python-etcd \
        python-conftool \
        etcd \
        python-etcd \
        python-conftool \
    && \
        apt-get clean && rm -rf /var/lib/apt/lists/*

USER nobody
