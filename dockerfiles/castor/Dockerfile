FROM docker-registry.wikimedia.org/wikimedia-stretch:latest

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install --yes \
        openssh-client \
        rsync \
    && rm -rf /var/lib/apt/lists/*

COPY src/ /castor
COPY run.bash /run.bash

USER nobody
ENTRYPOINT ["/run.bash"]
