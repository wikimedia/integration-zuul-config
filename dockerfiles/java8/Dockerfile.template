FROM {{ "ci-stretch" | image_tag }}

RUN {{ "openjdk-8-jdk-headless" | apt_install }}

# Install a more recent Maven version
COPY KEYS /tmp/KEYS
COPY apache-maven-3.5.2-bin.tar.gz.asc /tmp/apache-maven-3.5.2-bin.tar.gz.asc
RUN {{ "gnupg wget" | apt_install }} \
    && cd /tmp \
    && wget http://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.5.2/apache-maven-3.5.2-bin.tar.gz \
    && gpg --batch --import /tmp/KEYS \
    && gpg --verify apache-maven-3.5.2-bin.tar.gz.asc \
    && tar -C /opt -zxf apache-maven-3.5.2-bin.tar.gz \
    && apt purge --yes gnupg wget \
    && rm -rf ~/.gnupg

# sonar:sonar does not support XDG_CACHE_HOME - T207046
ENV SONAR_USER_HOME=$XDG_CACHE_HOME/sonar

# maven wrapper does not support XDG_CACHE_HOME - T218099
ENV MAVEN_USER_HOME=$XDG_CACHE_HOME/maven

COPY mvn /usr/local/bin/mvn
ENV MAVEN_BIN=/opt/apache-maven-3.5.2/bin/mvn
RUN /usr/local/bin/mvn --version

COPY settings.xml /settings.xml
COPY run.sh /run.sh

USER nobody
WORKDIR /src
CMD ["clean package"]
ENTRYPOINT ["/run.sh"]
