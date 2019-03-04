FROM {{ "java8" | image_tag }}

USER root
# wikidata/query/rdf runs wikidata/query/gui tests. gui uses
# releng/npm-browser-test which comes with Chromium, Firefox and PhantomJS all
# properly configured.
#
# The rdf repo also run the gui tests, and thus require PhantomJs (for
# grunt-contrib-qunit 2.0) and Chrome dependencies for grunt-contrib-qunit 3.0
# which relies on Puppeteer.
# See: gui build broken by grunt-contrib-qunit 3.0: T209776
RUN echo "deb [check-valid-until=no] http://snapshot.debian.org/archive/debian-security/20181208T014322Z/ stretch/updates main " \
    > /etc/apt/sources.list.d/snapshot-chromium.list
RUN {{ "chromium='71*' phantomjs" | apt_install }}

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=1,
# When set, used by "gui" qunit tests to configure Puppeteer. Should be removed
# once gui updates to Puppeteer 1.8.0+
ENV CHROME_BIN=/usr/bin/chromium
# For Puppeteer 1.8.0+:
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Can't change namespaces inside an unprivileged container, then we are already
# in a namespace so just disable Chromium sandboxing.
# See: a732ac637dfe8f82902b2762aeab11f0e612c832
#
# Note: Puppeteer downloads its own Chrome, but the flag would be useful if we
# later find a way to use the Chromium Debian Package (via
# PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true)
ENV CHROMIUM_FLAGS="--no-sandbox"

USER nobody

# wikidata/query/rdf relies on npm
# See <https://docs.npmjs.com/misc/config#environment-variables>
# and <https://docs.npmjs.com/cli/cache>
ENV NPM_CONFIG_CACHE=/cache

# phantomjs crashes when there is no DISPLAY
ENV QT_QPA_PLATFORM=offscreen
