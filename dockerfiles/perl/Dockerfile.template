FROM {{ "ci-stretch" | image_tag }}

RUN {{ "perl" | apt_install }}

USER nobody
WORKDIR /src
ENTRYPOINT ["/usr/bin/perl"]
