FROM wmfreleng/npm-test-stretch:latest

USER root
RUN git clone --depth 1 https://gerrit.wikimedia.org/r/integration/jenkins /tmp/jenkins \
    && cp /tmp/jenkins/bin/npm-install-dev.py /npm-install-dev.py \
    && rm -rf /tmp/jenkins

USER nobody
COPY run-for-deploy.sh /run-for-deploy.sh
ENTRYPOINT ["/run-for-deploy.sh"]
