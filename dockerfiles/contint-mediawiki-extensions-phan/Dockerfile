FROM docker-registry.wikimedia.org/wikimedia-jessie:latest

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
        # TODO Instead of --force-yes actually att the pub key from puppet?!!
        apt-get install --yes --force-yes --no-install-recommends \
            # Needed for phan
            php7.0-cli \
            # Needed for composer to install things from dist
            php7.0-zip \
            # Needed for mediawiki
            php-ast php7.0-mbstring php7.0-xml && \
        apt-get remove --yes software-properties-common apt-transport-https && \
        apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/* && \
        # INSTALL composer
        git clone --depth 1 https://gerrit.wikimedia.org/r/p/integration/composer.git /srv/composer && \
        rm -rf /srv/composer/.git && \
        # INSTALL phan
        mkdir /srv/phan && \
        cd /srv/phan && \
        /srv/composer/vendor/bin/composer require etsy/phan:0.8 && \
        rm -rf ~/.composer && \
        # SETUP jenkins user
        groupadd -g 500 wikidev && \
        # This is the uid and gid of the jenkins-deploy user for CI
        useradd -u 2947 -g 500 \
            --home-dir /var/lib/jenkins \
            --create-home jenkins && \
        mkdir /var/lib/jenkins/log && \
        chown -R 2947:500 /var/lib/jenkins/log

USER jenkins
WORKDIR /var/lib/jenkins

#TODO can't clone mediawiki in the image build, as we need master....?
RUN     PHAN=/srv/phan/vendor/bin/phan && \
        #NOTE: Can't remove ~/mediawiki/.git to save space as it is needed while running phan
        git clone --depth 1 https://gerrit.wikimedia.org/r/p/mediawiki/core.git ~/mediawiki && \
        cd ~/mediawiki && \
        /srv/composer/vendor/bin/composer install --no-dev && \
        rm -rf ~/.composer

ENTRYPOINT /bin/bash /run.sh

COPY run.sh /run.sh