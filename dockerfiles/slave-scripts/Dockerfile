FROM wmfreleng/ci-jessie:latest

USER root

COPY .cache-buster-slave-scripts /.cache-buster-slave-scripts

RUN git clone --depth 1 https://gerrit.wikimedia.org/r/p/integration/jenkins.git /srv/deployment/integration/slave-scripts && \
    rm -rf /srv/deployment/integration/slave-scripts/.git

USER nobody
