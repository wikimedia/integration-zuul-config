# castor-load
# Load cache from central repository
set -u

[[ $JOB_NAME == *'docker'* ]] && is_docker=1 || is_docker=''

if [ $is_docker ]; then
    # For containers we mount $WORKSPACE/cache from the host to /cache in the
    # container. It is also the value of XDG_CACHE_HOME
    DEST="/cache"
else
    DEST="$HOME"
fi

echo "Syncing..."
rsync \
  --archive \
  --delete-delay \
  --compress \
  --contimeout 3 \
  rsync://castor02.integration.eqiad.wmflabs:/caches/"$CASTOR_NAMESPACE"/ "$DEST" \
  || :
echo -e "\nDone"
