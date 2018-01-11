FROM {{ "composer" | image_tag }}

USER nobody
COPY run.sh /run.sh
ENTRYPOINT /bin/bash /run.sh
