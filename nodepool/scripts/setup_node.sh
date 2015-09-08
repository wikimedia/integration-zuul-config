#!/bin/bash
set -e

if [ -z "$1" ]; then
	echo "Usage: $0 <hostname>"
	exit 1
fi;

set -u

HOSTNAME="$1"
echo "Placeholder Nodepool setup script"
echo "Hostname: $1"
