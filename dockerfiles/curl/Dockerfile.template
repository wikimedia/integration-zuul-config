FROM {{ "ci-stretch" | image_tag }}

RUN {{ "curl" | apt_install }}

USER nobody

ENTRYPOINT ["curl"]
CMD ["--help"]
