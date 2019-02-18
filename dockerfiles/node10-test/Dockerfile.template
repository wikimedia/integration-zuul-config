# Docker image with nodejs and jsduck installed.
# Executes 'npm run {cmd:test}' in /src.

FROM {{ "node10" | image_tag }}

USER root

# build-essential: for compilation.
# python: for node-gyp.
# ruby: for jsduck.
RUN {{ "ruby ruby2.3 ruby2.3-dev rubygems-integration python build-essential" | apt_install }} \
    && gem install --no-rdoc --no-ri jsduck

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

# Headless Chrome requires --no-sandbox in order to work in a Docker environment.
# This is here rather than node10-test-browser, because this should also apply
# to tools that have an embedded Chromium build.
# https://docs.travis-ci.com/user/chrome#sandboxing
# https://github.com/GoogleChrome/puppeteer/blob/v1.11.0/docs/troubleshooting.md
ENV CHROMIUM_FLAGS="--no-sandbox"

WORKDIR /src
COPY run.sh /run.sh
ENTRYPOINT ["/run.sh"]
