#!/bin/bash
set -euxo pipefail

cd /src

cargo rustdoc
# This file causes rsync errors because it has
# restrictive permissions
rm target/doc/.lock
