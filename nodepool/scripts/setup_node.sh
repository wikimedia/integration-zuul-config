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

# https://review.openstack.org/#/c/222759/
sudo mkdir -p /opt/nodepool-scripts

echo "Cloning integration/config"
sudo mkdir -p /opt/git/integration
sudo git clone /srv/git/integration/config.git /opt/git/integration
sudo git -C /opt/git/integration/config remote set-url origin https://gerrit.wikimedia.org/r/p/integration/config.git
sudo git -C /opt/git/integration/config pull

echo "Running puppet"
sudo git -C /puppet pull
sudo /usr/local/bin/puppet-apply /opt/git/integration/config/dib/puppet/ciimage.pp
