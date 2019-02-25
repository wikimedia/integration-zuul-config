FROM {{ "ci-stretch" | image_tag }}

COPY sury-php.gpg /etc/apt/trusted.gpg.d/php.gpg
# Sury uses https and requires lsb per https://packages.sury.org/php/README.txt
RUN {{ "apt-transport-https" | apt_install }} && \
 echo "deb https://packages.sury.org/php/ stretch main" > /etc/apt/sources.list.d/php.list
