FROM wmfreleng/ci-jessie:latest

# Install nodejs-legacy to provide /usr/bin/node alias
RUN apt-get update && \
    apt-get install --yes \
        nodejs-legacy npm \
        # ruby/etc for jsduck
        ruby ruby2.1 ruby2.1-dev rubygems-integration build-essential && \
        gem install --no-rdoc --no-ri jsduck && \
        apt-get remove -y build-essential && apt-get autoremove -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# DO NOT CHANGE VERSION WITHOUT INVOLVING Krinkle OR hashar
RUN npm install -g npm@3.8.3

# If no volume is mounted, make sure /cache exists
RUN install --directory /cache --owner nobody

USER nobody

# See <https://docs.npmjs.com/misc/config#environment-variables>
# and <https://docs.npmjs.com/cli/cache>
ENV NPM_CONFIG_CACHE=/cache
ENV BABEL_CACHE_PATH=$XDG_CACHE_HOME/babel-cache.json

ENTRYPOINT ["npm"]
CMD ["--help"]
