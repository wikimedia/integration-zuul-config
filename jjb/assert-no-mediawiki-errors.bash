set -eu

# These log files are enabled by mediawiki:includes/DevelopmentSettings.php,
# as included by Quibble's local_settings.php file.
#
# For example:
#
#  $wgDBerrorLog = "$logDir/mw-dberror.log";
#  $wgDebugLogGroups['exception'] = "$logDir/mw-error.log";
#  $wgDebugLogGroups['error'] = "$logDir/mw-error.log";
#
# TODO: Add mw-dberror.log to ERROR_FILES (T246358)
#
ERROR_FILES=( mw-error.log )
echo "Asserting empty files: ${ERROR_FILES[*]}"

log_files="$( cd "$WORKSPACE/log"; ls "${ERROR_FILES[@]}" 2> /dev/null || :)"
if [ ! "$log_files" ]; then
    echo "No error files created by MediaWiki. GOOD"
    exit 0
fi

echo "Dumping file(s) $log_files"
set +e
    # Use `grep --color . file list` to ensure that file names appear next
    # to log messages
    (cd "$WORKSPACE/log"; grep --color . "${ERROR_FILES[@]}" 2> /dev/null)
set -e
echo -e "MediaWiki emitted some errors. Check output above."
exit 1
