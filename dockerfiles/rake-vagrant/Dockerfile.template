FROM {{ "rake" | image_tag }}

USER root
RUN {{ "rsync zlib1g-dev" | apt_install }}

USER nobody
