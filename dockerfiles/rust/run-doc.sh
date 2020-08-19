#!/bin/bash
set -euxo pipefail

cd /src

cargo rustdoc
