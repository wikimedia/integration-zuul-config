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

CI_CONFIG='integration/config'
echo "Cloning $CI_CONFIG from image mirror"
sudo git clone "/srv/git/${CI_CONFIG}.git" "/opt/git/${CI_CONFIG}"
echo "Pulling from Gerrit"
sudo git -C "/opt/git/${CI_CONFIG}" remote set-url origin "https://gerrit.wikimedia.org/r/p/${CI_CONFIG}.git"
sudo git -C "/opt/git/${CI_CONFIG}" pull

echo "Running puppet"
sudo git -C /puppet pull
sudo /usr/local/bin/puppet-apply /opt/git/integration/config/dib/puppet/ciimage.pp

echo "apt-get upgrade && clean"
sudo apt-get -q update
sudo apt-get -V -q -y upgrade
sudo apt-get clean
