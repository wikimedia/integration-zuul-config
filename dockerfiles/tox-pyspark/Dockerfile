FROM wmfreleng/tox:latest

USER root

# liblapack3 and libgomp1 are specifically needed for search/MjoLniR which
# runs numerical algorithms
RUN apt-get update && \
    apt-get install --yes \
        maven \
        wget \
        gnupg \
        liblapack3 \
        libgomp1 \
        && \
    rm -rf /var/lib/apt/lists/*

COPY KEYS /tmp/KEYS
COPY spark-2.1.0-bin-hadoop2.6.tgz.asc /tmp/spark-2.1.0-bin-hadoop2.6.tgz.asc

RUN cd /tmp && \
    wget https://archive.apache.org/dist/spark/spark-2.1.0/spark-2.1.0-bin-hadoop2.6.tgz && \
    gpg --import /tmp/KEYS && \
    gpg --verify spark-2.1.0-bin-hadoop2.6.tgz.asc && \
    tar -C /opt -zxf spark-2.1.0-bin-hadoop2.6.tgz && \
    rm spark-2.1.0-bin-hadoop2.6.tgz* KEYS && \
    cd -

# ivy, used by spark to source our internal jar dependencies from archiva, needs a proper home
# directory or it bails.
RUN adduser testrunner

USER testrunner
WORKDIR /src
ENTRYPOINT /bin/bash /run.sh
COPY run.sh /run.sh
