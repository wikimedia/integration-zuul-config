set -eu +x

ssh_config=($TRIGGERED_SSH_CONNECTION)
REMOTE_INSTANCE="${ssh_config[2]}"

# Destination in the central cache
DEST="/srv/jenkins-workspace/caches/${CASTOR_NAMESPACE}"

echo "Creating directory holding cache:"
mkdir -v -p "${DEST}"

remote_cache_dir="${TRIGGERED_WORKSPACE}/cache"
cache_dir='/cache'

echo -e "Syncing cache\nFrom.. ${REMOTE_INSTANCE}:${remote_cache_dir}\nTo.... ${DEST}"
set -x
rsync \
  --archive \
  --compress \
  --rsh="/usr/bin/ssh -a -T -o ConnectTimeout=6 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" \
  --rsync-path="docker run --rm -i --volume ${remote_cache_dir}:/${cache_dir} --entrypoint=/usr/bin/rsync wmfreleng/castor:v2017.10.30.17.08" \
  --delete-delay \
  jenkins-deploy@"${REMOTE_INSTANCE}:/${cache_dir}/" "${DEST}"

echo -e "\nDone"
