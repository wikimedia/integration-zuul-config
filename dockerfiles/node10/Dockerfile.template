# Docker image with plain nodejs and npm.

FROM {{ "ci-stretch" | image_tag }}

USER root

# Use Node 10 instead of Node 6
RUN echo "deb http://apt.wikimedia.org/wikimedia stretch-wikimedia component/node10" > /etc/apt/sources.list.d/stretch-node10.list \
    && {{ "nodejs" | apt_install }} \
    && git clone --depth 1 https://gerrit.wikimedia.org/r/p/integration/npm.git /srv/npm \
    && rm -rf /srv/npm/.git \
    && ln -s /srv/npm/bin/npm-cli.js /usr/bin/npm

USER nobody

ENTRYPOINT ["npm"]
CMD ["--help"]
