#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <hostname>"
    exit 1
fi;

set -u

HOSTNAME="$1"
echo "${0} (hostname $HOSTNAME)"
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

echo "Refresh /puppet repo"
sudo git -C /puppet pull

echo "Setting up apt configuration"
# Needs ::apt first so we get jessie-wikimedia and jessie-backports configured
# and pinned. Else our packages are not up-to-date / not found.
sudo /usr/local/bin/puppet-apply /opt/git/integration/config/dib/puppet/aptconf.pp
echo "apt-get update and dist-upgrade"
sudo apt-get -q update

echo "Running puppet"
sudo /usr/local/bin/puppet-apply /opt/git/integration/config/dib/puppet/ciimage.pp

echo "apt-get dist-upgrade && clean"
sudo apt-get -V -q -y --force-yes -o 'DPkg::Options::=--force-confold' dist-upgrade
sudo apt-get clean

# T113342, left over leases delay instances boot
echo "Deleting DHCP leases"
sudo rm -fv /var/lib/dhcp/dhclient.*.leases

echo "Syncing filesystem"
sync

echo "${0} complete (hostname: ${HOSTNAME})"
