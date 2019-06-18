FROM {{ "composer-php72" | image_tag }}

User root

# Create directory where we're going to install to
RUN install --directory --mode 777 /opt/phan

USER nobody

COPY run.sh /run.sh
ENTRYPOINT ["/run.sh"]
