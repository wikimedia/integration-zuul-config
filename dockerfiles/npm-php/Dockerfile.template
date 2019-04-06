FROM {{ "npm-stretch" | image_tag }}

USER root

RUN {{ "php-cli php-mbstring" | apt_install }}

USER nobody
