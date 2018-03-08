# Inheritance! Make sure npm-test-stretch is in sync with npm-test.
FROM {{ "npm-test" | image_tag }} as npm-test

FROM {{ "npm-stretch" | image_tag }}

USER nobody
COPY --from=npm-test /run.sh /run.sh
COPY --from=npm-test /run-oid.sh /run-oid.sh
COPY --from=npm-test /npm-install-dev.py /npm-install-dev.py
ENTRYPOINT ["/run.sh"]
