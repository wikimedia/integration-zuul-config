FROM {{ "npm-test" | image_tag }}

USER root

RUN {{ "libsasl2-dev librdkafka-dev/jessie-wikimedia" | apt_install }}

USER nobody
