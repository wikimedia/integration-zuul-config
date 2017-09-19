FROM docker-registry.wikimedia.org/wikimedia-jessie:latest

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        # The r language itself
        r-base \
        # Needed to build lintr
        make gcc g++ ca-certificates gfortran liblapack-dev libxml2-dev libssl-dev libcurl4-openssl-dev \
        && \
    Rscript -e 'install.packages("devtools", repos="http://cran.rstudio.com/")' && \
    Rscript -e 'devtools::install_github("jimhester/lintr@v1.0.1")' && \
    apt-get remove --yes make gcc g++ gfortran liblapack-dev libssl-dev libcurl4-openssl-dev && \
    apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/*

# TODO git & ca-certificates should probably be in some base CI image...
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends git && \
    apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir -m 777 /log && mkdir -m 777 /src

USER nobody
WORKDIR /src
ENTRYPOINT /bin/bash /run.sh
COPY run.sh /run.sh