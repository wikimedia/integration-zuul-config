FROM {{ "tox" | image_tag }}

USER root
RUN {{ "build-essential libevent-dev" | apt_install }}

USER nobody
