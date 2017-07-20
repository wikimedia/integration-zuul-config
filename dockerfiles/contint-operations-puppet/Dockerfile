FROM docker-registry.wikimedia.org/wikimedia-jessie:latest

ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
        build-essential \
        bundler \
        git \
        locales \
        python-dev \
        python-pip \
        rubygems-integration \
        rake \
        ruby \
        ruby-dev && \
        apt-get clean && rm -rf /var/lib/apt/lists/*  && \
        pip install pip==8.1.2 && \
        pip install tox==1.9.2 setuptools && \
        echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
        locale-gen && \
        groupadd -g 500 wikidev && \
        # This is the uid and gid of the jenkins-deploy user for CI
        useradd -u 2947 -g 500 \
            --home-dir /var/lib/jenkins \
            --create-home jenkins

COPY cache /var/lib/jenkins/.cache

RUN chown -R 2947:500 /var/lib/jenkins/.cache

USER jenkins
WORKDIR /var/lib/jenkins
ENTRYPOINT /bin/bash /run.sh

COPY run.sh /run.sh
