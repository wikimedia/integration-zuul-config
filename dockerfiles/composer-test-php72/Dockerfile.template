FROM {{ "composer-test" | image_tag }} as composer-test

FROM {{ "composer-php72" | image_tag }}

USER nobody
COPY --from=composer-test /run.sh /run.sh
ENTRYPOINT /bin/bash /run.sh
