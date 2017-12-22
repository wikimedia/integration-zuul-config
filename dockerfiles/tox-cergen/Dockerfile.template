FROM {{ "tox" | image_tag }}

USER root
RUN {{ "openjdk-8-jre-headless" | apt_install }}

USER nobody
