#!/bin/bash

set -eux -o pipefail

install --mode 777 --directory cache log src

repos=(
    wikimedia/fundraising/crm
    wikimedia/fundraising/crm/civicrm-buildkit
    wikimedia/fundraising/crm/civicrm
)
for repo in "${repos[@]}"; do
    docker run --rm -it \
        --volume /"$(pwd)"/src://src \
        --entrypoint=git \
        docker-registry.wikimedia.org/releng/civicrm:latest \
        clone --depth 1 \
            "https://gerrit.wikimedia.org/r/${repo}.git" "/src/${repo}"
done

docker run --rm -it \
    --volume /"$(pwd)"/cache://cache \
    --volume /"$(pwd)"/log://log \
    --volume /"$(pwd)"/src://src \
    --env BUILD_NUMBER=fake_build_number \
    --env BUILD_TAG=fake_build_tag \
    --env JOB_ID=fake_job_id \
    --env WORKSPACE='' \
    docker-registry.wikimedia.org/releng/civicrm:latest
