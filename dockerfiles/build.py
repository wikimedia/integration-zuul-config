#!/usr/bin/env python3

import argparse
import sys
from datetime import datetime
import os.path
from glob import glob
import logging
import subprocess

BASE_DIR = os.path.dirname(__file__)
DOCKER_TAG_DATE = datetime.utcnow().strftime("v%Y.%m.%d.%H.%M")
DOCKER_HUB_ACCOUNT = 'wmfreleng'


class DockerBuilder(object):

    def run(self):
        self.log = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO)

        self.parse_args()
        if self.args.Dockerfile:
            dockerfiles = [
                os.path.join(f, 'Dockerfile')
                for f in self.args.Dockerfile
            ]
        else:
            dockerfiles = self.find_docker_files()
        return all(map(self.build, dockerfiles))

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('Dockerfile', nargs='*', default=[])
        self.args = parser.parse_args()

    def find_docker_files(self):
        return glob(os.path.join(BASE_DIR, '*/Dockerfile'))

    def build(self, Dockerfile):
        self.log.info('Building %s' % Dockerfile)

        image_name = os.path.dirname(Dockerfile)

        if os.path.exists(os.path.join(image_name, 'prebuild.sh')):
            self.log.info("Prebuild script")
            subprocess.check_call('./prebuild.sh', cwd=image_name)

        IMG = '/'.join([DOCKER_HUB_ACCOUNT, image_name])
        TAGGED_IMG = ':'.join([IMG, DOCKER_TAG_DATE])

        cmd = ['docker', 'build', '-t', TAGGED_IMG, '-f', 'Dockerfile', '.']
        self.log.info(' '.join(cmd))
        subprocess.check_call(cmd, cwd=image_name)

        cmd = ['docker', 'tag', TAGGED_IMG, '%s:latest' % IMG]
        self.log.info(' '.join(cmd))
        subprocess.check_call(cmd, cwd=image_name)

        return True


if __name__ == '__main__':
    builder = DockerBuilder()
    if not builder.run():
        sys.exit(1)
