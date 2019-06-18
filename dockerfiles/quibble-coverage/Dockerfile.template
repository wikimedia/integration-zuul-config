FROM {{ "quibble-stretch-php72" | image_tag }}

USER root

#
# CI utilities to generate per patches coverage
#
RUN mkdir -p /opt/composer-tmp /opt/phpunit-patch-coverage \
    && chown nobody:nogroup /opt/composer-tmp /opt/phpunit-patch-coverage
USER nobody
RUN cd /opt/phpunit-patch-coverage \
    && COMPOSER_HOME=/opt/composer-tmp composer require -- mediawiki/phpunit-patch-coverage 0.0.10 \
    && find /opt/composer-tmp -mindepth 1 -delete
USER root
RUN rmdir /opt/composer-tmp \
    && ln -s /opt/phpunit-patch-coverage/vendor/bin/phpunit-patch-coverage /usr/local/bin/phpunit-patch-coverage
COPY clover-edit.py /usr/local/bin/clover-edit
COPY phpunit-suite-edit.py /usr/local/bin/phpunit-suite-edit
COPY phpunit-junit-edit.py /usr/local/bin/phpunit-junit-edit
COPY mediawiki-coverage.sh /usr/local/bin/mediawiki-coverage
COPY mwext-phpunit-coverage.sh /usr/local/bin/mwext-phpunit-coverage
COPY mwext-phpunit-coverage-patch.sh /usr/local/bin/mwext-phpunit-coverage-patch

USER nobody
