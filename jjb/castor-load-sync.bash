# castor-load
# Load cache from central repository
set -u

[[ $JOB_NAME == *'docker'* ]] && is_docker=1 || is_docker=''

if [ $is_docker ]; then
    # For containers we mount $WORKSPACE/cache from the host to /cache in the
    # container. It is also the value of XDG_CACHE_HOME
    DEST="/cache"
    # cache might persist between builds on the Docker slaves
    rsync_delete='--delete-delay'
else
    DEST="$HOME"
    # On Nodepool it is guaranteed to be empty. Deleting would wipe
    # /home/jenkins/workspace!
fi

echo "Syncing..."
rsync \
  --archive \
  ${rsync_delete:-} \
  --compress \
  --contimeout 3 \
  rsync://castor02.integration.eqiad.wmflabs:/caches/"$CASTOR_NAMESPACE"/ "$DEST" \
  || :
echo -e "\nDone"
