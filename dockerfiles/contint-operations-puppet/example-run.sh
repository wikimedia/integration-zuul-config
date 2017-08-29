docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=operations/puppet \
    --env ZUUL_COMMIT=56e788486bee2da19495660ad12753bc57d246bb \
    --env ZUUL_REF=refs/changes/89/374389/1 \
    --volume /$(pwd)/log://var/lib/jenkins/log \
     wmfreleng/operations-puppet