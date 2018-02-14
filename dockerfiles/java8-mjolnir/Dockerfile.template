FROM {{ "java8" | image_tag }}

USER root
RUN {{ "liblapack3 libgomp1" | apt_install }}
USER nobody
