FROM {{ 'npm' | image_tag }}

USER root

# Add a script that is able to install solely the devDependencies
RUN git clone --depth 1 https://gerrit.wikimedia.org/r/integration/jenkins /tmp/jenkins \
    && cp /tmp/jenkins/bin/npm-install-dev.py /npm-install-dev.py \
    && rm -rf /tmp/jenkins

USER nobody
COPY run.sh /run.sh
COPY run-oid.sh /run-oid.sh
ENTRYPOINT ["/run.sh"]
