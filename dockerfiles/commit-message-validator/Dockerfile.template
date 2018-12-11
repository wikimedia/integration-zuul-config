FROM {{ "ci-stretch" | image_tag }}

USER root
RUN {{ "python3 python3-pip" | apt_install }} \
    && install --owner=nobody --group=nogroup \
          --directory /opt/commit-message-validator \
    && ln -s \
          /opt/commit-message-validator/bin/commit-message-validator \
          /usr/local/bin/commit-message-validator

USER nobody
RUN pip3 install --no-cache-dir --system --prefix /opt/commit-message-validator commit-message-validator

USER nobody
WORKDIR /src
ENV PYTHONPATH=/opt/commit-message-validator/lib/python3.5/site-packages
ENTRYPOINT set -x \
    && pip3 install --upgrade --no-cache-dir --system --prefix /opt/commit-message-validator commit-message-validator \
    && /opt/commit-message-validator/bin/commit-message-validator
