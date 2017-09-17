FROM wmfreleng/php:latest

USER root

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
        # Required by sury per https://packages.sury.org/php/README.txt
        apt-transport-https lsb-release ca-certificates && \
    echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list && \
    # Only update the source we have added to save time
    apt-get update -o Dir::Etc::sourcelist="sources.list.d/php.list" -o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="0" && \
    apt-get install --yes --no-install-recommends \
        # Needed for composer to install things from dist
        php7.0-zip \
        # Needed for mediawiki
        php-ast php7.0-mbstring php7.0-xml && \
    apt-get remove --yes \
        apt-transport-https lsb-release ca-certificates && \
    apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/* && \
    rm /etc/apt/sources.list.d/php.list

USER php