FROM wmfreleng/ci-jessie:latest

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        zuul \
        # pin python-pbr https://phabricator.wikimedia.org/T153877
        python-pbr=0.8.2-1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY .cache-buster-integration-jenkins /.cache-buster-integration-jenkins

RUN git clone --depth 1 https://gerrit.wikimedia.org/r/integration/jenkins /tmp/jenkins && \
    cp /tmp/jenkins/etc/zuul-clonemap.yaml /zuul-clonemap.yaml && \
    rm -rf /tmp/jenkins

USER nobody

ENTRYPOINT ["zuul-cloner"]
CMD ["--help"]
