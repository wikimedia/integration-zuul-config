# castor-load
# Load cache from central repository
set -u

[[ $TRIGGERED_JOB_NAME == *'docker'* ]] && is_docker=1 || is_docker=''

if [ $is_docker ]; then
    DEST="$WORKSPACE"
else
    DEST="$HOME"
fi

echo "Syncing..."
rsync \
  --archive \
  --compress \
  --contimeout 3 \
  rsync://castor02.integration.eqiad.wmflabs:/caches/"$CASTOR_NAMESPACE"/ "$DEST" \
  || :
echo -e "\nDone"
