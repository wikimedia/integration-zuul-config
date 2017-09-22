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

FROM docker-registry.wikimedia.org/wikimedia-jessie:latest

ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
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
        locale-gen

COPY --from=builder /tmp/cache /srv/workspace/.cache
COPY bundle-config /srv/workspace/.cache/bundle-config

RUN chown -R nobody /srv/workspace/.cache && \
          mkdir -p /tmp/cache && \
          mv /srv/workspace/.cache/puppet /tmp/cache/puppet && \
          mkdir -p /tmp/cache/puppet/.bundle && \
          mv /srv/workspace/.cache/bundle-config /tmp/cache/puppet/.bundle/config && \
          mv /srv/workspace/.cache/tox /tmp/cache/puppet/.tox

USER nobody
WORKDIR /srv/workspace
ENTRYPOINT /bin/bash /run.sh

COPY run.sh /run.sh
