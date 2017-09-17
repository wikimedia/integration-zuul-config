FROM wmfreleng/php:latest

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
            # For the add-apt-repository command
            software-properties-common \
            # For using a https repo
            apt-transport-https && \
        # This repo means we can install php7.0
        add-apt-repository http://packages.sury.org/php/ && \
        apt-get update && \
        # TODO Instead of --force-yes actually get the pub key from puppet?!!
        apt-get install --yes --force-yes --no-install-recommends \
            # Needed for phan
            php7.0-cli && \
        apt-get remove --yes software-properties-common && \
        apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY .cache-buster-composer /.cache-buster-composer

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
        git \
        ca-certificates && \
    git clone --depth 1 https://gerrit.wikimedia.org/r/p/integration/composer.git /srv/composer && \
    rm -rf /srv/composer/.git && \
    apt-get remove --yes \
         git \
         ca-certificates \
         apt-transport-https && \
    apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd -r composer && useradd --no-log-init -r -g composer composer

USER composer

ENTRYPOINT ["/srv/composer/vendor/bin/composer"]
CMD ["help"]