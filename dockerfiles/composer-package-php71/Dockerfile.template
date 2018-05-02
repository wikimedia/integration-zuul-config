FROM {{ "composer-package" | image_tag }} as composer-package

FROM {{ "composer-php71" | image_tag }}

USER nobody
COPY --from=composer-package /run.sh /run.sh
ENTRYPOINT /bin/bash /run.sh
