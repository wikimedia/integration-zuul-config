FROM {{ "tox" | image_tag }}

USER root
RUN {{ "librdkafka-dev" | apt_install }}

USER nobody
