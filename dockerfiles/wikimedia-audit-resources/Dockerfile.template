FROM {{ "ci-stretch" | image_tag }}

USER root
RUN {{ "firefox-esr python3 python3-virtualenv xvfb xauth" | apt_install }}

USER nobody
# Initial clone, we'll do a pull when running so we're not
# constantly rebuilding this image just for every commit.
RUN git clone https://gerrit.wikimedia.org/r/integration/audit-resources src
ENV DISPLAY=:94

COPY run.sh /run.sh
ENTRYPOINT ["/run.sh"]
