FROM wmfreleng/ci-jessie:latest

# Just runs `doxygen` in /src
# Graphviz is used to generate call graphs.
RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
        doxygen graphviz && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER nobody

WORKDIR /src

ENTRYPOINT ["doxygen"]
