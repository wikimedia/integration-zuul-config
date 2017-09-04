FROM docker-registry.wikimedia.org/wikimedia-jessie:latest

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        zuul \
        # zuul doesn't pull this in automatically but clearly needs it
        git \
        # pin python-pbr https://phabricator.wikimedia.org/T153877
        python-pbr=0.8.2-1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY .cache-buster-integration-jenkins /.cache-buster-integration-jenkins

RUN git clone --depth 1 https://gerrit.wikimedia.org/r/integration/jenkins /tmp/jenkins && \
    cp /tmp/jenkins/etc/zuul-clonemap.yaml /zuul-clonemap.yaml && \
    rm -rf /tmp/jenkins

RUN groupadd -r zuul-cloner && useradd --no-log-init -r -g zuul-cloner zuul-cloner

USER zuul-cloner

ENTRYPOINT ["zuul-cloner"]
CMD ["--help"]
