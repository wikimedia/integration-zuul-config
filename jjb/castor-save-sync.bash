set -eu +x

ssh_config=($TRIGGERED_SSH_CONNECTION)
REMOTE_INSTANCE="${ssh_config[2]}"

# Destination in the central cache
DEST="/srv/jenkins-workspace/caches/${CASTOR_NAMESPACE}"

echo "Ensure cache directories exist on remote $REMOTE_INSTANCE"
ssh -q -a -T \
  -o ConnectTimeout=6 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no \
  jenkins@"${REMOTE_INSTANCE}" \
  'mkdir -v -p .cache/composer .composer/cache .m2/repository .cache/pip .npm workspace/vendor/bundle'

echo "Creating directory holding cache:"
mkdir -v -p "${DEST}"

echo -e "Syncing cache\nFrom.. ${REMOTE_INSTANCE}\nTo.... ${DEST}"
rsync \
  --archive \
  --compress \
  --rsh="ssh -a -T  -o ConnectTimeout=6 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" \
  --delete-delay \
  --relative \
  jenkins@"${REMOTE_INSTANCE}":.cache/composer :.composer/cache :.m2/repository :.cache/pip :.npm :workspace/vendor/bundle "${DEST}/"

echo -e "\nDone"
