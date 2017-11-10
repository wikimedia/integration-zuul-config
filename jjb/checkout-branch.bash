# Attempt to figure out MediaWiki branch being used and fetch it out
# if the extension has the same branch
if [[ "$MEDIAWIKI_ENVIRONMENT" == "beta"* ]]; then
  export MEDIAWIKI_API_URL="https://en.wikipedia.beta.wmflabs.org/w/api.php"
elif [ "$MEDIAWIKI_ENVIRONMENT" = "mediawiki" ]; then
  export MEDIAWIKI_API_URL="https://www.mediawiki.org/w/api.php"
elif [ "$MEDIAWIKI_ENVIRONMENT" = "test" ]; then
  export MEDIAWIKI_API_URL="https://test.wikipedia.org/w/api.php"
else
  echo "MEDIAWIKI_ENVIRONMENT $MEDIAWIKI_ENVIRONMENT not supported!"
  exit 1
fi
MEDIAWIKI_GIT_BRANCH=$(/srv/deployment/integration/slave-scripts/bin/mw-api-siteinfo.py "$MEDIAWIKI_API_URL" git_branch)

git checkout -f "origin/$MEDIAWIKI_GIT_BRANCH" || {{
    echo "origin/$MEDIAWIKI_GIT_BRANCH branch does not exist."
    echo "Fallbacking to master branch..."
    MEDIAWIKI_GIT_BRANCH='master'
    git checkout -f origin/$MEDIAWIKI_GIT_BRANCH
}}
git reset --hard "origin/$MEDIAWIKI_GIT_BRANCH"
git clean -x -q -d -f
