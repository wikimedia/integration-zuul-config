FROM wmfreleng/tox

USER root
RUN apt-get update && \
    apt-get install --yes \
        openjdk-8-jre-headless && \
    rm -rf /var/lib/apt/lists/*

USER nobody
