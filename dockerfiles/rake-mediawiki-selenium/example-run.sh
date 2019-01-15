#!/bin/bash

install --mode 777 --directory cache log

docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r/p \
    --env ZUUL_PROJECT=mediawiki/extensions/Wikibase \
    --env ZUUL_REF=master \
    --env BROWSER=chrome \
    --env MEDIAWIKI_ENVIRONMENT=beta \
    --env selenium_user_beta=foobar \
    --volume /"$(pwd)"/cache://cache\
    --volume /"$(pwd)"/log://log \
    docker-registry.wikimedia.org/releng/rake-mediawiki-selenium
