#!/bin/bash

/usr/sbin/gearmand -l stderr &

function terminate_gearmand() {
    kill "$(pidof gearmand)"
}

trap terminate_gearmand EXIT

/run.sh "${@}"
