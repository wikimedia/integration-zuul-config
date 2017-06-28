# Note: described in the parameters: section above
if [ "$ZUUL_PIPELINE" != 'gate-and-submit' -a "$ZUUL_PIPELINE" != 'postmerge' ]; then
    echo "Only saving cache for gate-and-submit or postmerge pipelines"
    exit 1
fi
