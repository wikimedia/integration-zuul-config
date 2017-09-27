FROM docker-registry.wikimedia.org/wikimedia-jessie:latest

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
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

RUN mkdir -m 777 /log && mkdir -m 777 /src

USER nobody
WORKDIR /src
ENTRYPOINT /bin/bash /run.sh
COPY run.sh /run.sh
