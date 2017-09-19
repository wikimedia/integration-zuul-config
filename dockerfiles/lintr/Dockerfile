FROM docker-registry.wikimedia.org/wikimedia-jessie:latest as builder

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        # The r language itself
        r-base \
        # Needed to build lintr
        make gcc g++ ca-certificates gfortran liblapack-dev libxml2-dev libssl-dev libcurl4-openssl-dev  \
        && \
    Rscript -e 'install.packages("devtools", repos="http://cran.rstudio.com/")' && \
    Rscript -e 'devtools::install_github("jimhester/lintr@v1.0.1")' && \
    apt-get remove --yes make gcc g++ gfortran liblapack-dev libxml2-dev libssl-dev libcurl4-openssl-dev && \
    apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY run.sh /run.sh

RUN groupadd -r lintr && useradd --no-log-init -r -g lintr lintr

#USER lintr
USER root

#ENTRYPOINT /bin/bash /run.sh
ENTRYPOINT /bin/bash