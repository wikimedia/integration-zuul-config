#!/bin/bash
set -euxo pipefail

LOG_DIR="/log"

if [[ -x ./run_pebble.sh ]]
then
    ./run_pebble.sh > "$LOG_DIR"/pebble.log

function terminate_pebble() {
    kill "$(pidof pebble)"
}
trap terminate_pebble SIGINT
trap terminate_pebble SIGTERM
trap terminate_pebble EXIT

/run.sh &
run_pid=$!
wait $run_pid
