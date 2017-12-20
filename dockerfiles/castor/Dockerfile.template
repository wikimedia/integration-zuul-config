FROM docker-registry.wikimedia.org/wikimedia-stretch

RUN {{ "rsync" | apt_install }} \
    && mkdir -p /castor

COPY castor-define-namespace.bash /castor/
COPY castor-load-sync.bash /castor/
COPY run.bash /run.bash

USER nobody
ENTRYPOINT ["/run.bash"]
