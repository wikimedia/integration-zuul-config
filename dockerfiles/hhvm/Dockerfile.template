FROM {{ "ci-stretch" | image_tag }}

USER root

RUN {{ "hhvm" | apt_install }}

COPY hhvm.ini /hhvm.ini

RUN tee --append /etc/hhvm/php.ini < /hhvm.ini \
    && touch /hhvm.hhbc \
    && chown nobody /hhvm.hhbc \
    && printf '<?php\necho "HHVM execution works\\n";\n' > /smoketest.php \
    && su -s '/bin/sh' -c 'hhvm /smoketest.php' nobody \
    && echo -n > /hhvm.hhbc \
    && rm /smoketest.php /hhvm.ini

# So that we always use the proper path even without a ini file (php -n)
ENV HHVM_REPO_CENTRAL_PATH=/hhvm.hhbc
RUN php -n -r 'echo "HHVM works without an ini file\n";'

USER nobody

ENTRYPOINT ["hhvm"]
CMD ["--help"]
