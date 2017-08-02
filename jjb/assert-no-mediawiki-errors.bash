set -eu

# The set of log files checked come from integration/jenkins
# mediawiki/conf.d/00_set_debug_log.php
#
# Namely:
#  $wgDBerrorLog = "$wmgMwLogDir/mw-dberror.log";
#  $wgDebugLogGroups['exception'] = "$wmgMwLogDir/mw-exception.log";
#  $wgDebugLogGroups['error'] = "$wmgMwLogDir/mw-error.log";
#
error_files=( mw-dberror.log mw-exception.log mw-error.log )
echo "Asserting empty files: ${error_files[*]}"

if [ "$ZUUL_BRANCH" != 'master' ]; then
	echo "Only for master branch"
	exit 0
fi

log_files="$( cd "$WORKSPACE/log"; ls "${error_files[@]}" 2> /dev/null || :)"
if [ ! "$log_files" ]; then
	echo "No error files. GOOD"
	exit 0
fi

echo "Dumping file(s) $log_files"
set +e
	(cd "$WORKSPACE/log"; grep --color . "${error_files[@]}" 2> /dev/null)
set -e
echo -e "MediaWiki emitted some errors. Check output above."
exit 1
