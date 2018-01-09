FROM {{ "ci-stretch" | image_tag }}
RUN {{ "build-essential rubygems-integration rake ruby ruby-dev bundler" | apt_install }}

COPY run.sh /run.sh
USER nobody
ENTRYPOINT ["/run.sh"]
