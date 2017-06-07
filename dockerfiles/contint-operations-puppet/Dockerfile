FROM debian:jessie
COPY share /opt

RUN apt-key add /opt/wikimedia-archive-keyring.gpg && \
    cp /opt/wikimedia.list /etc/apt/sources.list.d/wikimedia.list && \
    cp /opt/wikimedia.pref /etc/apt/preferences.d/wikimedia.pref

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
        build-essential \
        git \
        rubygems-integration \
        rake \
        ruby2.1 \
        ruby2.1-dev \
        bundler \
        ruby-rspec \
        cucumber \
        python3 \
        python3-dev \
        python3-tk \
        python-dev \
        python-pip \
        libmysqlclient-dev \
        libxml2-dev \
        libxslt1-dev \
        libffi-dev \
        libssl-dev \
        && \
        pip install pip==8.1.2 && \
        pip install tox==1.9.2 setuptools && \
        groupadd -g 500 wikidev && \
        useradd -u 2947 -g 500 --home-dir /var/lib/jenkins --create-home jenkins

USER jenkins
WORKDIR /var/lib/jenkins
ENTRYPOINT /bin/bash /run.sh

COPY contint-operations-puppet/run.sh /run.sh
