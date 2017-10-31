FROM wmfreleng/tox:latest

USER root

COPY KEYS /tmp/KEYS
COPY spark-2.1.0-bin-hadoop2.6.tgz.asc /tmp/spark-2.1.0-bin-hadoop2.6.tgz.asc

# liblapack3 and libgomp1 are specifically needed for search/MjoLniR which
# runs numerical algorithms
RUN apt-get update && \
    apt-get install --yes \
        openjdk-7-jre-headless \
        liblapack3 \
        libgomp1 \
        wget \
        && \
    rm -rf /var/lib/apt/lists/* && \
    cd /tmp && \
    wget https://archive.apache.org/dist/spark/spark-2.1.0/spark-2.1.0-bin-hadoop2.6.tgz && \
    gpg --import /tmp/KEYS && \
    gpg --verify spark-2.1.0-bin-hadoop2.6.tgz.asc && \
    tar -C /opt -zxf spark-2.1.0-bin-hadoop2.6.tgz && \
    rm spark-2.1.0-bin-hadoop2.6.tgz* KEYS && \
    apt-get purge --yes wget

# ivy, used by spark to source our internal jar dependencies from
# archiva.wikimedia.org, needs a proper home directory or it bails.
RUN adduser --disabled-password --gecos "" testrunner

USER testrunner
ENV SPARK_HOME /opt/spark-2.1.0-bin-hadoop2.6
