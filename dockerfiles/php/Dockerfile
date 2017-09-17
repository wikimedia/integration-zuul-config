FROM docker-registry.wikimedia.org/wikimedia-jessie:latest

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
            php7.0-cli && \
        apt-get remove --yes software-properties-common && \
        apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd -r php && useradd --no-log-init -r -g php php

USER php

ENTRYPOINT ["php"]
CMD ["--help"]