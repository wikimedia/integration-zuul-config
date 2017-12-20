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
# On the sender, run rsync in a container (--rsync-path) to have it run has
# user 'nobody'.
rsync \
  --archive \
  --compress \
  --rsh="/usr/bin/ssh -a -T -o ConnectTimeout=6 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" \
  --rsync-path="docker run --rm -i --volume ${remote_cache_dir}:${cache_dir} --entrypoint=/usr/bin/rsync docker-registry.wikimedia.org/releng/castor:0.1.0" \
  --delete-delay \
  jenkins-deploy@"${REMOTE_INSTANCE}:${cache_dir}/" "${DEST}"

echo -e "\nDone"
