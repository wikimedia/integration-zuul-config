FROM {{ "ci-stretch" | image_tag }}

# php is for filters, and mbstring+xml are required by MediaWiki
RUN {{ "doxygen graphviz php-cli php-mbstring php-xml" | apt_install }}

COPY run.sh /run.sh

USER nobody
ENTRYPOINT ["/run.sh"]
