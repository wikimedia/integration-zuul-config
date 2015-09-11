#!/bin/bash
set -e

if [ -z "$1" ]; then
	echo "Usage: $0 <hostname>"
	exit 1
fi;

set -u

HOSTNAME="$1"
echo "Hostname: $HOSTNAME"
sudo hostname $HOSTNAME
echo "127.0.0.1 $HOSTNAME" | sudo tee -a /etc/hosts
