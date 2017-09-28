set -eu

# The set of log files checked come from integration/jenkins
# mediawiki/conf.d/00_set_debug_log.php
#
# Namely:
#  $wgDBerrorLog = "$wmgMwLogDir/mw-dberror.log";
#  $wgDebugLogGroups['exception'] = "$wmgMwLogDir/mw-exception.log";
#  $wgDebugLogGroups['error'] = "$wmgMwLogDir/mw-error.log";
#
ERROR_FILES=( mw-dberror.log mw-exception.log mw-error.log )
echo "Asserting empty files: ${ERROR_FILES[*]}"

# The minimum RELx_xxx version for which we want to run this test
REL_MAJOR=1
REL_MINOR=30

# The minimum wmf/1.x.0-wmf.xx version for which we want to run this test
WMF_MAJOR=30
WMF_MINOR=12

# A valid version is a version > wmf/1.WMF_MAJOR.0-wmf.WMF_MINOR
valid_wmf_version() {
    local version major minor
    version="$1"

    major=${version%.*.*}
    major=${major##*.}

    minor=${version##*.}

    if (( major == WMF_MAJOR )) && (( minor >= WMF_MINOR )); then
        return 0
    elif (( major > WMF_MAJOR )); then
        return 0
    else
        return 1
    fi
}

# A valid version is a version > REL{REL_MAJOR}_{REL_MINOR}
valid_rel_version() {
    local version major minor
    version="$1"
    major=${version%%_*}
    minor=${version##*_}

    if (( major == REL_MAJOR )) && (( minor >= REL_MINOR )); then
        return 0
    elif (( major > REL_MAJOR )); then
        return 0
    else
        return 1
    fi
}

# Ensures that this is a ZUUL_BRANCH for which we want this to be a valid test
valid_version() {
    local version wmf_version rel_version

    version="$1"

    # Master is valid
    if [[ "$version" == "master" ]]; then
        return 0
    fi

    # Is this is a wmf/something
    wmf_version="${version#wmf\/}"
    if (( ${#version} != ${#wmf_version} )); then
        valid_wmf_version "$wmf_version" && return 0
    fi

    # Is this is a RELsomething
    rel_version="${version#REL}"
    if (( ${#version} != ${#rel_version} )); then
        valid_rel_version "$rel_version" && return 0
    fi

    # Unidentified version: invalid
    return 1
}

if ! valid_version "$ZUUL_BRANCH"; then
    printf 'Test not for branch: %s\n' "$ZUUL_BRANCH"
    exit 0
fi

log_files="$( cd "$WORKSPACE/log"; ls "${ERROR_FILES[@]}" 2> /dev/null || :)"
if [ ! "$log_files" ]; then
    echo "No error files. GOOD"
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
