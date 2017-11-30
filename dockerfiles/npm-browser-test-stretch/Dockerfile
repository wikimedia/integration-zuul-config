FROM wmfreleng/npm-browser-test:latest as npm-browser-test

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

# Firefox always write to $HOME/.mozilla which is not available to the nobody
# user. Provide a basic wrapper that points HOME to a temp directory.
# See https://github.com/karma-runner/karma-firefox-launcher/issues/28
RUN /bin/echo -e '#!/bin/sh\nHOME=/tmp/firefox\nexport HOME\nexec /usr/bin/firefox "$@"' > /usr/local/bin/firefox && \
    chmod +x /usr/local/bin/firefox

USER nobody
ENV DISPLAY=:94
# For karma-chrome-launcher
ENV CHROME_BIN=/usr/bin/chromium
ENV FIREFOX_BIN=/usr/local/bin/firefox

# Can't change namespaces inside an unprivileged container, then we are already
# in a namespace so just disable Chromium sandboxing
ENV CHROMIUM_FLAGS="--no-sandbox"

COPY --from=npm-browser-test /run-with-xvfb.sh /run-with-xvfb.sh
ENTRYPOINT ["/run-with-xvfb.sh"]
