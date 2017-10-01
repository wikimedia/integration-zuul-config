FROM wmfreleng/ci-stretch:latest

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
        php7.0-cli && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER nobody

ENTRYPOINT ["php"]
CMD ["--help"]
