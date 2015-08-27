#!/usr/bin/env python2
import os
import shlex
import subprocess
import sys
import time

# https://wikitech.wikimedia.org/wiki/Nodepool#Diskimage
#
# XXX add a switch to be able to set either of:
# DIB_OFFLINE=1
# DIB_DEBIAN_USE_DEBOOTSTRAP_CACHE=1


class WikimediaDib(object):

    def main(self):

        elements = [
            # Built-in
            'debian',
            'debian-systemd',
            'cloud-init-datasources',
            'vm',
            'devuser',
            # Custom
            'wikimedia-networking',
            'nodepool-base',
            ]

        release = 'jessie'

        image_type = 'qcow2'

        # Qemu fails if image names contains ':'
        # https://bugs.launchpad.net/ubuntu/+source/qemu/+bug/1216009
        image_filename = '-'.join([
            'image',
            release,
            time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
            ])

        script_dir = 'scripts'

        cache_dir = '/mnt/dib/cache'

        env = os.environ.copy()
        env.update({
            'DIB_IMAGE_NAME': image_filename,

            'NODEPOOL_SCRIPTDIR': script_dir,

            'DIB_IMAGE_CACHE': cache_dir,
            'QEMU_IMG_OPTIONS': 'compat=0.10',

            # debian element
            'DIB_RELEASE': release,
            'DIB_DISTRIBUTION_MIRROR': 'http://mirrors.wikimedia.org/debian/',

            # cloud-init-datasources
            'DIB_CLOUD_INIT_DATASOURCES': 'Ec2',

            # devuser element
            'DIB_DEV_USER_USERNAME': 'jenkins',
            'DIB_DEV_USER_AUTHORIZED_KEYS': 'dib_jenkins_id_rsa.pub',
            }
        )

        if 'ELEMENTS_PATH' in env:
            env['ELEMENTS_PATH'] += ':' + 'elements'
        else:
            env['ELEMENTS_PATH'] = 'elements'

        cmd = ('disk-image-create -t %s --no-tmpfs -o %s %s' %
               (image_type, image_filename, ' '.join(elements)))

        try:
            c = subprocess.Popen(shlex.split(cmd), env=env)
        except OSError as e:
            raise Exception("Failed to run '%s': '%s'" %
                            (cmd, e.strerror))

        c.wait()
        return c.returncode


if __name__ == '__main__':
    builder = WikimediaDib()
    ret = builder.main()
    if ret:
        sys.exit("Image building failed")
