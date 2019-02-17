FROM {{ "ci-stretch" | image_tag }} as pebble-builder

USER root

RUN {{ "golang-1.11-go" | apt_install }}
WORKDIR /root
RUN /usr/lib/go-1.11/bin/go get -d github.com/letsencrypt/pebble/... && \
    CGO_ENABLED=0 GOOS=linux /usr/lib/go-1.11/bin/go build -a -ldflags '-extldflags "-static" -w -s' ./go/src/github.com/letsencrypt/pebble/cmd/pebble/

USER nobody

FROM {{ "tox" | image_tag }}

USER root
COPY --from=pebble-builder /root/pebble /usr/local/bin/pebble

USER nobody
