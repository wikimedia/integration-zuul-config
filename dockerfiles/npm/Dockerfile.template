FROM {{ "ci-jessie" | image_tag }}

# DO NOT CHANGE VERSION WITHOUT INVOLVING Krinkle OR hashar
ARG NPM_VERSION="3.8.3"

# Install nodejs-legacy to provide /usr/bin/node alias
#
# build-essential for compilation
# python-minimal for node-gyp
# ruby/etc for jsduck
RUN {{ "nodejs-legacy npm ruby ruby2.1 ruby2.1-dev rubygems-integration python-minimal build-essential" | apt_install }} \
    && npm install -g npm@${NPM_VERSION} \
    && apt -y purge npm \
    && apt-get -y autoremove --purge \
    && gem install --no-rdoc --no-ri jsduck \
    # if no volume is mounted, make sure /cache exists
    && install --directory /cache --owner nobody

USER nobody

# Configure various known softwares that don't honor XDG cache dir
# so that they don't break when using the default of HOME:/nonexistent.
#
# These will write to /cache, which is re-used across builds via Castor.
# - npm http cache, <https://docs.npmjs.com/cli/cache>
ENV NPM_CONFIG_cache=$XDG_CACHE_HOME
# - https://babeljs.io/docs/en/babel-register/#babel-cache-path
ENV BABEL_CACHE_PATH=$XDG_CACHE_HOME/babel-cache.json
#
# These will write to /tmp, which is not preserved.
# - For instanbuljs/nyc, https://phabricator.wikimedia.org/T212602
ENV SPAWN_WRAP_SHIM_ROOT=$XDG_CONFIG_HOME

# Never check for npm self-update, https://phabricator.wikimedia.org/T213014
ENV NPM_CONFIG_update_notifier=false

ENTRYPOINT ["npm"]
CMD ["--help"]
