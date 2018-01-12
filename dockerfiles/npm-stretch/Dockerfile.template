# Debian stretch lacks npm, so we get our npm@3.8.3 from our Jessie based image
FROM {{ "npm" | image_tag }} as npm-jessie

FROM {{ "ci-stretch" | image_tag }}
COPY --from=npm-jessie /usr/local/lib/node_modules/npm/ /usr/local/lib/node_modules/npm/
# Manually link since COPY copies symlink destination instead of the actual symlink
RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm

# Install nodejs-legacy to provide /usr/bin/node alias
#
# build-essential for compilation
# python-minimal for node-gyp
# ruby/etc for jsduck
RUN {{ "nodejs-legacy python-minimal ruby ruby-dev rubygems-integration build-essential" | apt_install }}

RUN gem install --no-rdoc --no-ri jsduck

# If no volume is mounted, make sure /cache exists
RUN install --directory /cache --owner nobody

USER nobody

ENV NPM_CONFIG_CACHE=/cache
ENV BABEL_CACHE_PATH=$XDG_CACHE_HOME/babel-cache.json

ENTRYPOINT ["npm"]
CMD ["--help"]
