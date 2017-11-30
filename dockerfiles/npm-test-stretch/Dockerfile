# Inheritance! Make sure npm-test-stretch is in sync with npm-test.

FROM wmfreleng/npm-test:latest as npm-test

FROM wmfreleng/npm-stretch:latest

USER nobody
COPY --from=npm-test /run.sh /run.sh
ENTRYPOINT ["/run.sh"]
