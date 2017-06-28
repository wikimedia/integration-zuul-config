# castor-load
# Load cache from central repository
set -u

echo "Syncing..."
rsync \
  --archive \
  --compress \
  --contimeout 3 \
  rsync://castor.integration.eqiad.wmflabs:/caches/${CASTOR_NAMESPACE}/ $HOME \
  || :
echo -e "\nDone"
