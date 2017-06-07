FROM debian:jessie-slim
COPY share /opt

RUN apt-key add /opt/wikimedia-archive-keyring.gpg && \
    cp /opt/wikimedia.list /etc/apt/sources.list.d/wikimedia.list && \
    cp /opt/wikimedia.pref /etc/apt/preferences.d/wikimedia.pref

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
        build-essential \
        bundler \
        git \
        libmysqlclient-dev \
        locales \
        python-dev \
        python-pip \
        rubygems-integration \
        rake \
        ruby \
        ruby-dev \
        && \
        pip install pip==8.1.2 && \
        pip install tox==1.9.2 setuptools && \
        echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
        locale-gen && \
        groupadd -g 500 wikidev && \
        # This is the uid and gid of the jenkins-deploy user for CI
        useradd -u 2947 -g 500 \
            --home-dir /var/lib/jenkins \
            --create-home jenkins

ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'
USER jenkins
WORKDIR /var/lib/jenkins
ENTRYPOINT /bin/bash /run.sh

COPY contint-operations-puppet/run.sh /run.sh
