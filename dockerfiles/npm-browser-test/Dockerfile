FROM wmfreleng/npm-test-stretch:latest

USER root
RUN apt-get update && \
    apt-get install --yes \
        chromium \
        firefox-esr \
        phantomjs \
        xvfb \
    && \
        apt-get clean && rm -rf /var/lib/apt/lists/*

COPY firefox /usr/local/bin/firefox

USER nobody
ENV DISPLAY=:94

# For karma-chrome-launcher
#
# Developers usually configure Chrome, so point it to Chromium
ENV CHROME_BIN=/usr/bin/chromium
# Firefox wrapper introduced above to set HOME to a writable directory
ENV FIREFOX_BIN=/usr/local/bin/firefox

# Can't change namespaces inside an unprivileged container, then we are already
# in a namespace so just disable Chromium sandboxing
ENV CHROMIUM_FLAGS="--no-sandbox"

COPY run-with-xvfb.sh /run-with-xvfb.sh
ENTRYPOINT ["/run-with-xvfb.sh"]
