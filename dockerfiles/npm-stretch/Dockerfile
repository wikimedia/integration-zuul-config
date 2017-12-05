# Debian stretch lacks npm, so we get our npm@3.8.3 from our Jessie based image
FROM wmfreleng/npm:latest as npm-jessie

FROM wmfreleng/ci-stretch:latest
COPY --from=npm-jessie /usr/local/lib/node_modules/npm/ /usr/local/lib/node_modules/npm/
# Manually link since COPY copies symlink destination instead of the actual symlink
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm

# python-minimal for node-gyp
# ruby/etc for jsduck
RUN apt-get update && \
    apt-get install --yes \
        nodejs-legacy \
        python-minimal \
        ruby ruby-dev rubygems-integration build-essential && \
        gem install --no-rdoc --no-ri jsduck && \
        apt-get remove -y build-essential && apt-get autoremove -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# If no volume is mounted, make sure /cache exists
RUN install --directory /cache --owner nobody

USER nobody

ENV NPM_CONFIG_CACHE=/cache
ENV BABEL_CACHE_PATH=$XDG_CACHE_HOME/babel-cache.json

ENTRYPOINT ["npm"]
CMD ["--help"]
