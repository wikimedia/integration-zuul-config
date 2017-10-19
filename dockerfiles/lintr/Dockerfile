FROM wmfreleng/ci-jessie:latest

RUN apt-get update && \
    apt-get install --yes \
        # The r language itself
        r-base \
        # Needed to build lintr
        make gcc g++ gfortran liblapack-dev libxml2-dev libssl-dev libcurl4-openssl-dev \
        && \
    Rscript -e 'install.packages("devtools", repos="http://cran.rstudio.com/")' && \
    Rscript -e 'devtools::install_github("jimhester/lintr@v1.0.1")' && \
    apt-get remove --yes make gcc g++ gfortran liblapack-dev libssl-dev libcurl4-openssl-dev && \
    apt-get autoremove --yes && apt-get clean && rm -rf /var/lib/apt/lists/*

USER nobody
WORKDIR /src
ENTRYPOINT /bin/bash /run.sh
COPY run.sh /run.sh
COPY lint.R /lint.R
