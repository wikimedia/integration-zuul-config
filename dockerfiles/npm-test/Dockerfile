FROM wmfreleng/npm:latest

USER root
RUN apt-get update && \
    apt-get install --yes \
        rsync \
    && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER nobody
COPY run.sh /run.sh
ENTRYPOINT ["/run.sh"]
