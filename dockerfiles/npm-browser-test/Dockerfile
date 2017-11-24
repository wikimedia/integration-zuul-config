FROM wmfreleng/npm-test:latest

USER root
RUN apt-get update && \
    apt-get install --yes \
        phantomjs \
        xvfb \
    && \
        apt-get clean && rm -rf /var/lib/apt/lists/*

USER nobody
ENV DISPLAY=:94
COPY run-with-xvfb.sh /run-with-xvfb.sh
ENTRYPOINT ["/run-with-xvfb.sh"]
