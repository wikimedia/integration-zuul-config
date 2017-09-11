FROM docker-registry.wikimedia.org/wikimedia-jessie:latest as builder

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
        git \
        ca-certificates \
        python-pip \
        pypy \
        && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ARG PIP_DISABLE_PIP_VERSION_CHECK=1

RUN pip install pip==8.1.2 && \
    apt-get remove --yes --purge python-pip && \
    ln -s /usr/local/bin/pip /usr/bin/pip && \
    pip install tox==2.5.0 && \
    pip install setuptools

RUN groupadd -g 500 wikidev && \
        # This is the uid and gid of the jenkins-deploy user for CI
        useradd -u 2947 -g 500 \
            --home-dir /var/lib/jenkins \
            --create-home jenkins && \
        mkdir /var/lib/jenkins/log && \
        mkdir /srv/src && \
        chown -R 2947:500 /var/lib/jenkins/log && \
        chown -R 2947:500 /srv/src

USER jenkins
WORKDIR /var/lib/jenkins
ENTRYPOINT /bin/bash /run.sh
COPY run.sh /run.sh
