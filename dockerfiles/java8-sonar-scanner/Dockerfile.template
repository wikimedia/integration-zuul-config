FROM {{ "java8" | image_tag }}

USER root
COPY KEYS /tmp/KEYS

ENV SONAR_SCANNER_VERSION=3.3.0.1492

RUN echo "deb http://apt.wikimedia.org/wikimedia stretch-wikimedia component/node10" > /etc/apt/sources.list.d/stretch-node10.list \
    && {{ "nodejs gnupg wget unzip curl jq" | apt_install }} \
    && git clone --depth 1 https://gerrit.wikimedia.org/r/p/integration/npm.git /srv/npm \
    && rm -rf /srv/npm/.git \
    && ln -s /srv/npm/bin/npm-cli.js /usr/bin/npm \
    && cd /tmp \
    && wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-$SONAR_SCANNER_VERSION.zip \
    && wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-$SONAR_SCANNER_VERSION.zip.asc \
    && gpg --batch --import /tmp/KEYS \
    && gpg --verify sonar-scanner-cli-$SONAR_SCANNER_VERSION.zip.asc \
    && unzip sonar-scanner-cli-$SONAR_SCANNER_VERSION.zip \
    && mv sonar-scanner-$SONAR_SCANNER_VERSION /opt/sonar-scanner \
    && apt purge --yes gnupg wget unzip \
    && rm -rf ~/.gnupg

USER nobody
WORKDIR /workspace/src
COPY poll-sonar-for-response.sh /usr/local/bin/poll-sonar-for-response
COPY run.sh /run.sh
CMD [ "--version" ]
ENTRYPOINT [ "/run.sh" ]
