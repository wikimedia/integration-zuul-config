# Docker image with nodejs, jsduck, and browsers installed.
# Executes 'npm run {cmd:test}' in /src.

FROM {{ "node10-test" | image_tag }}

USER root

# browsers for tools that use headless chrome, and for selenium tests
RUN echo "deb [check-valid-until=no] http://snapshot.debian.org/archive/debian-security/20181208T014322Z/ stretch/updates main " \
    > /etc/apt/sources.list.d/snapshot-chromium.list
RUN {{ "chromium='71*' chromium-driver='71*' firefox-esr phantomjs xvfb ffmpeg" | apt_install }}
COPY firefox /usr/local/bin/firefox

USER nobody

# For karma-chrome-launcher
#
# Developers usually configure Chrome, so point it to Chromium
ENV CHROME_BIN=/usr/bin/chromium
# For karma-firefox-launcher
#
# Firefox wrapper introduced above to set HOME to a writable directory
ENV FIREFOX_BIN=/usr/local/bin/firefox

COPY run-with-xvfb.sh /run-with-xvfb.sh
