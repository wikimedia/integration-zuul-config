#!/bin/bash
#
# https://wikitech.wikimedia.org/wiki/Nodepool#Diskimage
#
# XXX add a switch to be able to set either of:
# DIB_OFFLINE=1
# DIB_DEBIAN_USE_DEBOOTSTRAP_CACHE=1

if [ ${DIB_DEBUG_TRACE:-0} -gt 0 ]; then
	set -x
fi
set -eu
set -o pipefail

ELEMENTS=(
	# Built-in
	'debian'
	'debian-systemd'
	'cloud-init-datasources'
	'vm'
	'devuser'
	# Custom
	'wikimedia'
	)
export DIB_COMMAND=${DIB_COMMAND:-'disk-image-create'}
export DIB_DISTRIBUTION_MIRROR=${DIB_DISTRUBITION_MIRROR:-'http://mirrors.wikimedia.org/debian/'}
export DIB_RELEASE=${DIB_RELEASE:-jessie}
export DIB_IMAGE_CACHE=${DIB_IMAGE_CACHE:-/srv/dib/cache}  # XXX should be unset by default
DATE=`date -u +'%Y%m%dT%H%M%SZ'`
export DIB_IMAGE_NAME=${DIB_IMAGE_NAME:-"image-${DIB_RELEASE}-${DATE}"}
export DIB_GIT_BARE_MIRRORS='/srv/git'

export IMAGE_TYPE="qcow2"

export DIB_CLOUD_INIT_DATASOURCES='Ec2'

export DIB_DEV_USER_USERNAME='jenkins'
export DIB_DEV_USER_AUTHORIZED_KEYS='dib_jenkins_id_rsa.pub'
export DIB_DEV_USER_SHELL='/bin/bash'

export DIB_WIKIMEDIA_PUPPET_SOURCE='./puppet'

export QEMU_IMG_OPTIONS='compat=0.10'  # XXX might not be needed

export NODEPOOL_SCRIPTDIR='../nodepool/scripts'


ELEMENTS_PATH=${ELEMENTS_PATH:-}
if [[ -z "$ELEMENTS_PATH" ]]; then
	export ELEMENTS_PATH='elements'
else
	export ELEMENTS_PATH="${ELEMENTS_PATH}:elements"
fi

$DIB_COMMAND -t "$IMAGE_TYPE" --no-tmpfs -o "$DIB_IMAGE_NAME" ${ELEMENTS[@]}
EXIT_CODE=$?
if [[ $EXIT_CODE -gt 0 ]]; then
	>&2 echo "Disk image creation failed (exit: $EXIT_CODE)"
	exit $EXIT_CODE
else
	echo "Disk image successful ${DIB_IMAGE_NAME}.${IMAGE_TYPE}"
fi
