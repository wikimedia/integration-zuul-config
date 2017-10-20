#!/bin/bash

set -e

# Copy castor shell scripts from the jjb snippets
mkdir -p "$(dirname "$0")"/src
cp -vf "$(dirname "$0")"/../../jjb/castor*.bash "$(dirname "$0")"/src
