FROM {{ "npm-test-stretch" | image_tag }}

USER root
RUN echo "deb [check-valid-until=no] http://snapshot.debian.org/archive/debian-security/20181208T014322Z/ stretch/updates main " \
    > /etc/apt/sources.list.d/snapshot-chromium.list
RUN {{ "chromium='71*' chromium-driver='71*' firefox-esr phantomjs xvfb ffmpeg" | apt_install }}

COPY firefox /usr/local/bin/firefox

USER nobody
ENV DISPLAY=:94

# For karma-chrome-launcher
#
# Developers usually configure Chrome, so point it to Chromium
ENV CHROME_BIN=/usr/bin/chromium
# For karma-firefox-launcher
#
# Firefox wrapper introduced above to set HOME to a writable directory
ENV FIREFOX_BIN=/usr/local/bin/firefox

# Can't change namespaces inside an unprivileged container, then we are already
# in a namespace so just disable Chromium sandboxing
ENV CHROMIUM_FLAGS="--no-sandbox"

COPY run-with-xvfb.sh /run-with-xvfb.sh
ENTRYPOINT ["/run-with-xvfb.sh"]
