FROM {{ "tox" | image_tag }}

USER root

COPY KEYS /tmp/KEYS
COPY spark-2.1.2-bin-hadoop2.6.tgz.asc /tmp/spark-2.1.2-bin-hadoop2.6.tgz.asc

# liblapack3 and libgomp1 are specifically needed for search/MjoLniR which
# runs numerical algorithms
RUN {{ "openjdk-8-jre-headless maven liblapack3 libgomp1 wget gnupg" | apt_install }} && \
    cd /tmp && \
    wget http://archive.apache.org/dist/spark/spark-2.1.2/spark-2.1.2-bin-hadoop2.6.tgz && \
    gpg --batch --import /tmp/KEYS && \
    gpg --verify spark-2.1.2-bin-hadoop2.6.tgz.asc && \
    tar -C /opt -zxf spark-2.1.2-bin-hadoop2.6.tgz && \
    rm spark-2.1.2-bin-hadoop2.6.tgz* KEYS && \
    apt-get purge --yes wget gnupg && \
    rm -rf ~/.gnupg

COPY log4j.properties /opt/spark-2.1.2-bin-hadoop2.6/conf/log4j.properties
COPY maven-settings.xml /etc/maven/settings.xml

USER nobody
ENV SPARK_HOME /opt/spark-2.1.2-bin-hadoop2.6
