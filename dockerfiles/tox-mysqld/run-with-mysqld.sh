#!/bin/bash
set -euxo pipefail

mkdir -p /tmp/mysqld/datadir
/usr/bin/mysql_install_db --user=nobody --datadir=/tmp/mysqld/datadir

mysqld="/usr/sbin/mysqld
    --verbose
    --datadir=/tmp/mysqld/datadir
    --log-error=/tmp/mysqld/error.log
    --pid-file=/tmp/mysqld/mysqld.pid
    --socket=/tmp/mysqld/mysqld.sock"
$mysqld &

function terminate_mysql() {
    kill "$(pidof mysqld)"
}
trap terminate_mysql SIGINT
trap terminate_mysql SIGTERM
trap terminate_mysql EXIT

/run.sh &
run_pid=$!
wait $run_pid
