#!/bin/bash

set -e

# Copy castor shell scripts from the jjb snippets
rm -fR "$(dirname "$0")"/src
mkdir -p "$(dirname "$0")"/src
for castor_script in castor-define-namespace.bash castor-load-sync.bash; do
    cp -vf "$(dirname "$0")"/../../jjb/"$castor_script" "$(dirname "$0")"/src
done
