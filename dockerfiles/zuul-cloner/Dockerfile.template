FROM {{ "tox" | image_tag }} AS build

USER root
RUN install --owner=nobody --group=nogroup --directory /opt/zuul

USER nobody
RUN virtualenv --python=python2.7 --always-copy /opt/zuul \
    && /opt/zuul/bin/pip2 install git+https://gerrit.wikimedia.org/r/integration/zuul.git#egg=zuul \
    && /opt/zuul/bin/zuul-cloner --version

FROM {{ "ci-stretch" | image_tag }}
RUN {{ "python2.7" | apt_install }}

RUN git clone --depth 1 https://gerrit.wikimedia.org/r/integration/jenkins /tmp/jenkins && \
    cp /tmp/jenkins/etc/zuul-clonemap.yaml /zuul-clonemap.yaml && \
    rm -rf /tmp/jenkins && \
    mkdir -p /opt/zuul

COPY --from=build /opt/zuul /opt/zuul

USER nobody
# Assert it is actually working
RUN /opt/zuul/bin/zuul-cloner --version
ENTRYPOINT ["/opt/zuul/bin/zuul-cloner"]
CMD ["--help"]
