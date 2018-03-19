FROM {{ "java8" | image_tag }}

USER root
RUN {{ "cmake gcc g++ make openjdk-8-jdk python" | apt_install }}
USER nobody
