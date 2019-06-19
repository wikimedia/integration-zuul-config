FROM {{ "quibble-stretch-php72" | image_tag }}

USER root

# Fresnel needs firefox-esr in order for Headless Chromium to work.
# There are numerous libs that Chromium only needs for headless mode
# and these are not statically linked in the distribution provioded by Google,
# and they also aren't specified by Debian as deps for 'chromium'.
# The full list is documented at:
#   https://github.com/GoogleChrome/puppeteer/blob/v1.12.2/docs/troubleshooting.md
# We've installed Firefox and Chrome together since 2015, so keep doing
# that for now.
# https://phabricator.wikimedia.org/T226078
RUN {{ "python build-essential firefox-esr" | apt_install }}

#
# Install Fresnel
#
RUN mkdir -p /opt/npm-tmp /opt/fresnel \
    && chown nobody:nogroup /opt/npm-tmp /opt/fresnel
USER nobody
RUN cd /opt/fresnel \
    && NPM_CONFIG_cache=/opt/npm-tmp NPM_CONFIG_update_notifier=false npm install fresnel@0.3.0 \
    && find /opt/npm-tmp -mindepth 1 -delete
USER root
RUN rm -rf /opt/npm-tmp \
    && ln -s /opt/fresnel/node_modules/.bin/fresnel /usr/local/bin/fresnel
COPY mediawiki-fresnel-patch.sh /usr/local/bin/mediawiki-fresnel-patch

# TODO: Move to quibble-stretch base image
#       and then remove from quibble-stretch-bundle/mwselenium.sh
ENV CHROMIUM_FLAGS="--no-sandbox"

# TODO: Fix Quibble to always export these, not just for qunit/wdio.
ENV MW_SERVER="http://127.0.0.1:9412"
ENV MW_SCRIPT_PATH="/"

# Unprivileged
RUN install --directory /workspace --owner=nobody --group=nogroup
USER nobody
WORKDIR /workspace
ENTRYPOINT ["/usr/local/bin/quibble"]
