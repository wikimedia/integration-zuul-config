FROM {{ "composer" | image_tag }}

USER root
RUN mkdir -p /opt/composer-tmp /opt/phpmetrics \
    && chown nobody:nogroup /opt/composer-tmp /opt/phpmetrics

USER nobody
RUN cd /opt/phpmetrics \
    && COMPOSER_HOME=/opt/composer-tmp composer require -- phpmetrics/phpmetrics 2.4.1 \
    && find /opt/composer-tmp -mindepth 1 -delete

USER root
RUN rmdir /opt/composer-tmp \
    && ln -s /opt/phpmetrics/vendor/bin/phpmetrics /usr/local/bin/phpmetrics

RUN install --directory /src --owner=nobody --group=nogroup
USER nobody
WORKDIR /src
ENTRYPOINT ["/usr/local/bin/phpmetrics"]

