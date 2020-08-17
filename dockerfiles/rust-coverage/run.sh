#!/bin/bash
set -euxo pipefail

cd /src

cargo tarpaulin --out=Xml --out=Html --output-dir=coverage --all-features
# Convert cobertura to clover format
xsltproc --output coverage/clover.xml /usr/bin/cobertura-clover-transform.xslt coverage/cobertura.xml
mv coverage/tarpaulin-report.html coverage/index.html
