#!/bin/bash

set -eu
set -o pipefail

# CI would set the log directories, else just create a ./log one
LOG_DIR=${LOG_DIR:-log}
mkdir -p "$LOG_DIR"
rm -f "$LOG_DIR"/{before.txt,current.txt}{,.gz}

_dir="$(dirname "$0")"
repodir="$(realpath "$_dir/..")"

# Runs zuul-server validation layout and log stderr to a file
function validate_layout() {
    local layout_file=$1
    local output_file=$2

    echo "Generating layout for $layout_file"
    echo "Logging to $output_file"
    set +e
    "$ZUUL_SERVER_BIN" \
        -c "$repodir"/tests/fixtures/zuul-dummy.conf \
        -t -l "$layout_file" \
        2>"$output_file"
    err=$?
    if [ $err != 0 ]; then
        cat "$output_file"
        echo "INVALID layout in $output_file"
        exit $err
    fi
    set -e
    echo "Done"
}

# Layout output is huge, so we compress it on completion
function compress_logs() {
    ( cd "$LOG_DIR" && {
        for txt_file in before.txt current.txt;
        do
            [ ! -f "$txt_file" ] && continue

            gzip --best --verbose "$txt_file"
        done
    })
}
trap compress_logs EXIT

# shellcheck source=/dev/null
source "$_dir"/setup-zuul-server.inc.sh

"$ZUUL_SERVER_BIN" --version

# Create a reference based on the current layout
validate_layout "$repodir/zuul/layout.yaml" "$LOG_DIR/current.txt"


# Get the previous layout

# Determine the previous commit to diff against
if [ -n "$(git -C "$repodir" status --porcelain -- zuul/layout.yaml)" ]; then
    # When there are changes in the working copy or changes have been staged,
    # compare with the latest commit.
    layout_prev_commit=HEAD
    echo "zuul/layout.yaml modified, will compare with latest commit (HEAD)"
elif [ -z "$(git -C "$repodir" show --name-only -m --first-parent --format=format: -- zuul/layout.yaml)" ]; then
    echo "HEAD does not change zuul/layout.yaml. No need for a diff."
    exit 0
else
    # Compare with the previous change that affected zuul/layout.yaml
    layout_prev_commit=$(git -C "$repodir" log --skip=1 -n1 --format='%H' zuul/layout.yaml)
    echo "zuul/layout.yaml previous commit: $layout_prev_commit"
fi

# The layout file must be in ./zuul/ to be able to load parameter functions
previous_layout=$(mktemp "$repodir"/zuul/zuul-layout-diff_XXXX)
trap 'rm -fR "$previous_layout"' EXIT

git -C "$repodir" show "$layout_prev_commit":zuul/layout.yaml > "$previous_layout"

validate_layout "$previous_layout" "$LOG_DIR/before.txt"


# Replacements to make diff easier to read
sed -i -e 's/^INFO:zuul\..*:Configured Pipeline Manager /Pipeline: /' \
    "$LOG_DIR"/before.txt "$LOG_DIR"/current.txt

echo "Looking for differences..."
(diff --show-function-line='^Pipeline: ' -u \
    "$LOG_DIR"/before.txt "$LOG_DIR"/current.txt
) | "$repodir"/.tox/zuul_tests/bin/diff-highlight
