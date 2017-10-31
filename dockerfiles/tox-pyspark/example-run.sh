#!/bin/bash

install --mode 777 --directory log
install --mode 777 --directory cache/{ivy2,pip}

docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=search/MjoLniR \
    --env ZUUL_COMMIT=master \
    --env ZUUL_REF=master \
    --volume /"$(pwd)"/log://log \
    --volume /"$(pwd)"/cache/ivy2:/home/testrunner/.ivy2 \
    --volume /"$(pwd)"/cache/pip:/cache/pip
     wmfreleng/tox-pyspark:latest
