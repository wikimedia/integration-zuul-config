#!/usr/bin/env python3

import argparse
from datetime import datetime
from glob import glob
import logging
import os.path
import subprocess
import sys
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCKER_TAG_DATE = datetime.utcnow().strftime("v%Y.%m.%d.%H.%M")
DOCKER_HUB_ACCOUNT = 'wmfreleng'


class DockerBuilder(object):

    def run(self):
        self.log = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO)

        self.parse_args()
        if self.args.directory:
            dockerfiles = [
                os.path.join(os.getcwd(), f, 'Dockerfile')
                for f in self.args.directory
            ]
        else:
            dockerfiles = self.find_docker_files()
        return all(map(self.build, dockerfiles))

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('directory', nargs='*', default=[])
        self.args = parser.parse_args()

    def find_docker_files(self):
        return glob(os.path.join(BASE_DIR, '*/Dockerfile'))

    def build(self, dockerfile):
        self.log.info('Building %s' % dockerfile)
        image_dir = os.path.dirname(dockerfile)

        image_name = os.path.relpath(image_dir, BASE_DIR)
        self.log.info('Image name: %s' % image_name)

        if os.path.exists(os.path.join(image_dir, 'prebuild.sh')):
            self.log.info("Prebuild script")
            subprocess.check_call(['bash', 'prebuild.sh'], cwd=image_dir)

        img = '/'.join([DOCKER_HUB_ACCOUNT, image_name])
        tagged_img = ':'.join([img, DOCKER_TAG_DATE])

        cmd = ['docker', 'build', '-t', tagged_img,
               os.path.dirname(dockerfile)]
        self.log.info(' '.join(cmd))
        subprocess.check_call(cmd)

        cmd = ['docker', 'tag', tagged_img, '%s:latest' % img]
        self.log.info(' '.join(cmd))
        subprocess.check_call(cmd)

        for f in glob.glob(os.path.join(image_dir, ".cache-buster*")):
            os.remove(f)

        return True


if __name__ == '__main__':
    builder = DockerBuilder()
    if not builder.run():
        sys.exit(1)
