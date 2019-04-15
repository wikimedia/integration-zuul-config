FROM {{ "quibble-stretch-php70" | image_tag }}

USER root

RUN {{ "libav-tools build-essential rubygems-integration ruby ruby-dev bundler" | apt_install }}

COPY mwselenium.sh /usr/local/bin/mwselenium

# Prevent Chromium caches to be in XDG_CACHE_HOME - T220948
ENV XDG_CONFIG_HOME=/tmp/xdg-config-home

# Unprivileged
USER nobody
WORKDIR /workspace
ENTRYPOINT ["/usr/local/bin/quibble", "--commands", "mwselenium"]
