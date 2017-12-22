FROM {{ "tox" | image_tag }}

USER root
# pywikibot requires a valid $HOME to write user-config.py to
RUN install \
        --mode 755 \
        --owner nobody \
        --group nogroup \
        --directory /home/nobody \
    && /usr/sbin/usermod --home /home/nobody nobody

USER nobody
