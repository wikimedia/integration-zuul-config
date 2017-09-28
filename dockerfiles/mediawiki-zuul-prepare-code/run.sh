#!/usr/bin/env bash

cd /src

# manual shell builder
echo $ZUUL_PROJECT > /tmp/deps.txt
echo -e $EXT_DEPENDENCIES >> /tmp/deps.txt
echo -e $SKIN_DEPENDENCIES > /tmp/deps_skins.txt

# builder: zuul-cloner
zuul-cloner --version
zuul-cloner \
    --color \
    --verbose \
    --map /zuul-clonemap.yaml \
    --workspace /src \
    --cache-dir /srv/git \
    https://gerrit.wikimedia.org/r/p \
    mediawiki/core \
    mediawiki/vendor \
    $(cat /tmp/deps.txt) \
    $(cat /tmp/deps_skins.txt)

# builder: ext-skins-submodules-update
find extensions skins -maxdepth 2 \
   -name .gitmodules \
   -execdir bash -xe -c '
       git submodule foreach git clean -xdff -q
       git submodule update --init --recursive
       git submodule status
       ' \;
