#!/bin/bash
set -euxo pipefail

export DISPLAY=:94
/usr/bin/Xvfb "$DISPLAY" -screen 0 1280x1024x24 -ac -nolisten tcp &
xvfb_pid=$!

/run.sh &
run_pid=$!

trap 'kill -SIGINT $run_pid; wait $run_pid' SIGINT
trap 'kill -SIGTERM $run_pid; wait $run_pid' SIGTERM
trap 'set +x; echo "Terminating Xvfb"; kill -SIGTERM $xvfb_pid; wait $xvfb_pid; echo Done; set -x' EXIT

wait $run_pid
