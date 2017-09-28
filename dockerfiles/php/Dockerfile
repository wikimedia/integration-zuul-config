FROM wmfreleng/ci-jessie:latest

COPY sury-php.gpg /etc/apt/trusted.gpg.d/php.gpg

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
        # Required by sury per https://packages.sury.org/php/README.txt
        apt-transport-https lsb-release && \
    echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list && \
    # Only update the source we have added to save time
    apt-get update -o Dir::Etc::sourcelist="sources.list.d/php.list" -o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="0" && \
    apt-get install --yes --no-install-recommends \
        php7.0-cli && \
    apt-get remove --yes \
        apt-transport-https lsb-release && \
    apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/* && \
    rm /etc/apt/sources.list.d/php.list

USER nobody

ENTRYPOINT ["php"]
CMD ["--help"]
