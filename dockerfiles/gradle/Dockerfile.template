FROM {{ "ci-stretch" | image_tag }}
RUN {{ "gradle" | apt_install }}

# Gradle requires a writable directory for caches, properties files, etc.
ENV GRADLE_USER_HOME=/var/local/gradle
RUN mkdir -p $GRADLE_USER_HOME \
    && chown nobody:nogroup $GRADLE_USER_HOME \
    && chmod 0700 $GRADLE_USER_HOME

USER nobody
ENTRYPOINT ["gradle"]
