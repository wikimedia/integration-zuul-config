#!/bin/sh
set -euxo pipefail

cd /src

cargo fmt -- --check
cargo clippy --all-features -- -D warnings
cargo test --all-features --verbose
