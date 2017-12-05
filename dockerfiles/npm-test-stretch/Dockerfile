# Inheritance! Make sure npm-test-stretch is in sync with npm-test.

FROM wmfreleng/npm-test:latest as npm-test

FROM wmfreleng/npm-stretch:latest

USER root
RUN apt-get update && \
    apt-get install --yes \
        rsync \
    && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER nobody
COPY --from=npm-test /run.sh /run.sh
ENTRYPOINT ["/run.sh"]
