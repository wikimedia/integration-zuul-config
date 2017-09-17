FROM docker-registry.wikimedia.org/wikimedia-jessie:latest

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
            git && \
        apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd -r git && useradd --no-log-init -r -g git git

USER git

ENTRYPOINT ["git"]
CMD ["--help"]