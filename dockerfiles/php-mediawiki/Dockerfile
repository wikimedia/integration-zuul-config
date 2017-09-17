FROM wmfreleng/php:latest

USER root

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
            # Cloning of repos
            git \
            # For the add-apt-repository command
            software-properties-common \
            # For using a https repo
            apt-transport-https && \
        # This repo means we can install php7.0
        add-apt-repository http://packages.sury.org/php/ && \
        apt-get update && \
        # TODO Instead of --force-yes actually get the pub key from puppet?!!
        apt-get install --yes --force-yes --no-install-recommends \
            # Needed for composer to install things from dist
            php7.0-zip \
            # Needed for mediawiki
            php-ast php7.0-mbstring php7.0-xml && \
        apt-get remove --yes software-properties-common apt-transport-https && \
        apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/*

USER php