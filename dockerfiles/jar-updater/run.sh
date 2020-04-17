#!/bin/bash

set -e

SCRIPT=/src/bin/update-refinery-source-jars

if [ ! -x "$SCRIPT" ]; then
    echo "$SCRIPT not found"
    echo "You must clone the source repository and volume mount it on /src"
    exit 1
fi

cd /src
exec "$SCRIPT"
