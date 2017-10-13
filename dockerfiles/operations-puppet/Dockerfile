FROM docker-registry.wikimedia.org/wikimedia-jessie:latest as builder

ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        ca-certificates \
        git \
    && \
    mkdir -p /tmp/cache && \
    git clone https://gerrit.wikimedia.org/r/operations/puppet /tmp/cache/puppet

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        build-essential \
        bundler \
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
        pip install tox==1.9.2 setuptools

COPY .cache-buster-operations-puppet /.cache-buster-operations-puppet

# Make all kinds of artifacts
RUN cd /tmp/cache/puppet && \
    git remote update && \
    git prune origin && \
    git reset --hard $(cut -f1 /.cache-buster-operations-puppet) && \
    git clean -xqdf && \
    git tag -f 'docker-head' && \
    git gc --prune=now && \
    bundle install --clean --path="/tmp/cache/bundle" && \
    TOX_TESTENV_PASSENV=PY_COLORS PY_COLORS=1 tox -v --notest && \
    mv .tox /tmp/cache/tox

FROM wmfreleng/ci-jessie:latest

ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        build-essential \
        bundler \
        python-dev \
        python-pip \
        rubygems-integration \
        rake \
        ruby \
        ruby-dev && \
        apt-get clean && rm -rf /var/lib/apt/lists/*  && \
        pip install pip==8.1.2 && \
        pip install tox==1.9.2 setuptools && \
        groupadd -g 500 wikidev && \
        # This is the uid and gid of the jenkins-deploy user for CI
        useradd -u 2947 -g 500 \
            --home-dir /var/lib/jenkins \
            --create-home jenkins

COPY --from=builder /tmp/cache /var/lib/jenkins/.cache
COPY bundle-config /var/lib/jenkins/.cache/bundle-config

RUN chown -R 2947:500 /var/lib/jenkins/.cache && \
          mkdir -p /tmp/cache && \
          mv /var/lib/jenkins/.cache/puppet /tmp/cache/puppet && \
          mkdir -p /tmp/cache/puppet/.bundle && \
          mv /var/lib/jenkins/.cache/bundle-config /tmp/cache/puppet/.bundle/config && \
          mv /var/lib/jenkins/.cache/tox /tmp/cache/puppet/.tox

USER jenkins
WORKDIR /var/lib/jenkins
ENTRYPOINT /bin/bash /run.sh

COPY run.sh /run.sh
