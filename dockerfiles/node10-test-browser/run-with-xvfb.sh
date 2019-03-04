#!/bin/bash
set -euxo pipefail

export DISPLAY=:94
/usr/bin/Xvfb "$DISPLAY" -screen 0 1280x1024x24 -ac -nolisten tcp &
xvfb_pid=$!

/usr/bin/chromedriver --url-base=/wd/hub --port=4444 &
chromedriver_pid=$!

function terminate_bg_process() {
    set +x

    kill -0 $xvfb_pid 2>/dev/null && {
        echo "Terminating Xvfb"
        kill -SIGTERM $xvfb_pid
        wait $xvfb_pid
        echo Done
    }

    kill -0 $chromedriver_pid 2>/dev/null && {
        echo "Terminating Chromedriver"
        kill -SIGTERM $chromedriver_pid
        # On a signal, Chromedriver exits with 127 + signal
        wait $chromedriver_pid || :
        echo Done
    }

    set -x
}

trap 'kill -SIGINT $run_pid $chromedriver_pid; wait $run_pid $chromedriver_pid' SIGINT
trap 'kill -SIGTERM $run_pid $chromedriver_pid; wait $run_pid $chromedriver_pid' SIGTERM
trap terminate_bg_process EXIT

/run.sh "${@}" &
run_pid=$!

wait $run_pid
