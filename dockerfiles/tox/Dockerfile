FROM wmfreleng/ci-jessie:latest

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
        python-pip \
        pypy \
        && \
    rm -rf /var/lib/apt/lists/*

ARG PIP_DISABLE_PIP_VERSION_CHECK=1

RUN pip install pip==8.1.2 && \
    apt-get remove --yes --purge python-pip && \
    ln -s /usr/local/bin/pip /usr/bin/pip && \
    pip install tox==2.5.0 && \
    pip install setuptools

USER nobody
WORKDIR /src
ENTRYPOINT /bin/bash /run.sh
COPY run.sh /run.sh
