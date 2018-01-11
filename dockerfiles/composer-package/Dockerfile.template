FROM {{ "composer" | image_tag }}

USER root
# Enable xdebug for PHPUnit coverage reports
RUN phpenmod xdebug

USER nobody
COPY run.sh /run.sh
ENTRYPOINT ["/run.sh"]
