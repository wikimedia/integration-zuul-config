FROM {{ "ci-src-setup-simple" | image_tag }} AS ci-src-setup-simple

FROM {{ "ci-stretch" | image_tag }}
COPY --from=ci-src-setup-simple /run.sh /ci-src-setup.sh

USER nobody
WORKDIR /src
ENTRYPOINT /ci-src-setup.sh && ! /usr/bin/git grep -E -I -f typos -- . ':(exclude)typos'
