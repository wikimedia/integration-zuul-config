set -eu +x
# castor-env
# Forge castor environement

# Replace slashes with dashes:
NS_PROJECT=${ZUUL_PROJECT////-}
NS_BRANCH=${ZUUL_BRANCH////-}

# Pill up MediaWiki extensions and skins caches together
if [[ "$ZUUL_PROJECT" =~ ^mediawiki/(extensions|skins)/ ]]; then
    NS_PROJECT="castor-mw-ext-and-skins"
fi

# Ex: mediawiki-core/REL1_26/tox-jessie
# Prefer TRIGGERED_JOB_NAME when it is set
NS_JOB=${TRIGGERED_JOB_NAME:-$JOB_NAME}

CASTOR_NAMESPACE="${NS_PROJECT}/${NS_BRANCH}/${NS_JOB}"

# Ex: mediawiki-core/REL1_26/tox-jessie
echo "declare -x CASTOR_NAMESPACE=\"$CASTOR_NAMESPACE\"" > castor-set-namespace.env
echo "Defined: CASTOR_NAMESPACE=\"$CASTOR_NAMESPACE\""
