FROM {{ "tox" | image_tag }}

USER root
RUN {{ "python-etcd python-conftool etcd" | apt_install }}

USER nobody
