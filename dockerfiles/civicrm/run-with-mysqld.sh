#!/bin/bash
set -euxo pipefail

mkdir -p /tmp/mysqld/datadir
/usr/bin/mysql_install_db --user=nobody --datadir=/tmp/mysqld/datadir

MYSQL_SOCKET=/var/run/mysqld/mysqld.sock

mysqld="/usr/sbin/mysqld
    --verbose
    --datadir=/tmp/mysqld/datadir
    --log-error=/tmp/mysqld/error.log
    --pid-file=/tmp/mysqld/mysqld.pid
    --socket=${MYSQL_SOCKET}"
$mysqld &

function terminate_mysql() {
    kill "$(pidof mysqld)"
}
trap terminate_mysql SIGINT
trap terminate_mysql SIGTERM
trap terminate_mysql EXIT

while [ "$(pidof mysqld)" ] && [ ! -e "$MYSQL_SOCKET" ]; do
    echo "Waiting for $MYSQL_SOCKET"
    sleep 1
done;

/run.sh "${@}" &

run_pid=$!
wait $run_pid
