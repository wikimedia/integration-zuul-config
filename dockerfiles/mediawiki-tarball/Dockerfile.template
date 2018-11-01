FROM {{ 'ci-stretch' | image_tag }}

USER root
RUN {{ "python3 python3-virtualenv python3-requests" | apt_install }} && \
    install --directory --mode 777 /opt/release

USER nobody
# Initial clone, we'll do a pull when running so we're not
# constantly rebuilding this image just for every commit.
RUN git clone https://gerrit.wikimedia.org/r/mediawiki/tools/release /opt/release
COPY run.sh /run.sh
ENTRYPOINT ["/run.sh"]
