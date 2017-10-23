#!/bin/bash

set -e

mkdir -p "$(dirname "$0")"/src
cp -vf "$(dirname "$0")"/../../jjb/castor*.bash "$(dirname "$0")"/src
