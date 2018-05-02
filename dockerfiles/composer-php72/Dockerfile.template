FROM {{ "composer" | image_tag }} as composer

FROM {{ "php72" | image_tag }}

COPY --from=composer /srv/composer /srv/composer
# Manually link since COPY copies symlink destination instead of the actual symlink
USER root
RUN ln -s /srv/composer/vendor/bin/composer /usr/bin/composer

RUN {{ "jq" | apt_install }}

USER nobody

ENTRYPOINT ["/srv/composer/vendor/bin/composer"]
CMD ["help"]
