FROM {{ "ci-stretch" | image_tag }}

RUN {{ "ruby ruby-dev build-essential" | apt_install }} \
    && gem install --no-rdoc --no-ri --clear-sources jsduck \
    && rm -fR /var/lib/gems/*/cache/*.gem \
    && apt -y purge build-essential ruby-dev \
    && apt-get -y autoremove --purge

USER nobody
COPY run.sh /run.sh
ENTRYPOINT ["/run.sh"]
