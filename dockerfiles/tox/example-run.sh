#!/bin/bash
declare -i err=0

install --mode 2777 --directory log
for project in analytics/quarry/web labs/tools/crosswatch; do
    docker run \
        --rm --tty \
        --env ZUUL_URL=https://gerrit.wikimedia.org/r \
        --env ZUUL_PROJECT="$project" \
        --env ZUUL_COMMIT=master \
        --env ZUUL_REF=master \
        --volume /"$(pwd)"/log://log \
         wmfreleng/tox:latest
    err+=$?
done

# Ensure we can compile 'netifaces' and a wheel is hold in the cache
docker run --rm --tty \
    --entrypoint=/bin/bash wmfreleng/tox:latest \
    -c 'pip install --disable-pip-version-check --target /src/install --cache-dir /src/cache -v netifaces && find /src/cache -name "netifaces-*.whl"'
err+=$?

if [ $err == 0 ]; then
    echo "[OK] all examples passed"
else
    echo "[KO] $err example(s) failed"
    exit 1
fi
