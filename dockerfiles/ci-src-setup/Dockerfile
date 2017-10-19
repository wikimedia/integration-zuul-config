FROM wmfreleng/ci-jessie:latest as clone-integration-jenkins

COPY .cache-buster-integration-jenkins /.cache-buster-integration-jenkins

RUN git clone --depth 1 https://gerrit.wikimedia.org/r/p/integration/jenkins.git /srv/jenkins && \
    rm -rf /srv/jenkins/.git


FROM wmfreleng/composer:latest as composer


FROM wmfreleng/ci-jessie

# wmfreleng/php
COPY sury-php.gpg /etc/apt/trusted.gpg.d/php.gpg

RUN apt-get update && \
    apt-get install --yes \
        # Required by sury per https://packages.sury.org/php/README.txt
        apt-transport-https lsb-release && \
    echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list && \
    # Only update the source we have added to save time
    apt-get update -o Dir::Etc::sourcelist="sources.list.d/php.list" -o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="0" && \
    apt-get install --yes \
        php7.0-cli && \
    apt-get remove --yes \
        apt-transport-https lsb-release && \
    apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/* && \
    rm /etc/apt/sources.list.d/php.list

# wmfreleng/php-mediawiki
RUN apt-get update && \
    apt-get install --yes \
        # Required by sury per https://packages.sury.org/php/README.txt
        apt-transport-https lsb-release && \
    echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list && \
    # Only update the source we have added to save time
    apt-get update -o Dir::Etc::sourcelist="sources.list.d/php.list" -o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="0" && \
    apt-get install --yes \
        # Needed for composer to install things from dist
        php7.0-zip \
        # Needed for mediawiki
        php-ast php7.0-mbstring php7.0-xml && \
    apt-get remove --yes --purge \
        apt-transport-https lsb-release && \
    apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/* && \
    rm /etc/apt/sources.list.d/php.list

# TODO python image?
# TODO is python2 and 3 needed for the slave scripts?
RUN apt-get update && \
    apt-get install --yes \
        python python3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# zuul-cloner
RUN apt-get update && \
    apt-get install --yes \
        zuul \
        # pin python-pbr https://phabricator.wikimedia.org/T153877
        python-pbr=0.8.2-1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=clone-integration-jenkins /srv/jenkins/bin /srv/slave-scripts
COPY --from=clone-integration-jenkins /srv/jenkins/etc/zuul-clonemap.yaml /srv/zuul-clonemap.yaml
COPY --from=composer /srv/composer /srv/composer

COPY setup-mw.sh /srv/setup-mw.sh
COPY setup-mwext.sh /srv/setup-mwext.sh

RUN mkdir -p /srv/deployment/integration/slave-scripts/etc && \
    ln -s /srv/slave-scripts /srv/deployment/integration/slave-scripts/bin && \
    ln -s /srv/zuul-clonemap.yaml /srv/deployment/integration/slave-scripts/etc/zuul-clonemap.yaml && \
    ln -s /srv/composer/vendor/bin/composer /usr/local/bin/composer

USER nobody
