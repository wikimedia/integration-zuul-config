#!/usr/bin/env python3

import argparse
from collections import defaultdict
import configparser
from datetime import datetime
from glob import glob
import json
import logging
import os.path
import re
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCKER_TAG_DATE = datetime.utcnow().strftime("v%Y.%m.%d.%H.%M")
DOCKER_HUB_ACCOUNT = 'wmfreleng'


class DockerBuilder(object):

    def __init__(self):
        self.deps_tree = {}
        self.stages = {}

    def run(self):
        self.parse_args()

        self.log = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=self.args.verbose)

        self.load_config()

        if self.args.directory:
            dockerfiles = [
                os.path.join(BASE_DIR, f, 'Dockerfile')
                for f in self.args.directory
            ]
        else:
            dockerfiles = self.find_docker_files()

        self.gen_deps_tree(dockerfiles)
        self.gen_staged_deps()
        if self.args.deps:
            print(json.dumps(self.deps_tree))
            return True
        if self.args.stages:
            print(json.dumps(self.stages))
            return True

        return all(map(self.build, dockerfiles))

    def load_config(self):
        config = configparser.ConfigParser()
        config.read([
            os.path.join(BASE_DIR, 'build.conf.default'),
            os.path.join(BASE_DIR, 'build.conf'),
        ])
        self.config = config

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-v', '--verbose', action='store_const',
            const=logging.DEBUG, default=logging.INFO)

        group = parser.add_mutually_exclusive_group()
        group.add_argument('directory', nargs='*', default=[])
        group.add_argument(
            '--deps', action='store_true',
            help='Dump images dependency tree and exit')
        group.add_argument(
            '--stages', action='store_true',
            help='Dump stages grouping sibling images')

        self.args = parser.parse_args()

    def find_docker_files(self):
        return sorted(glob(os.path.join(BASE_DIR, '*/Dockerfile')))

    def gen_deps_tree(self, files):
        froms = {}
        for f in files:
            image_name = 'wmfreleng/' + os.path.basename(os.path.dirname(f))
            with open(f) as fp:
                froms[image_name] = []
                for l in fp.readlines():
                    m = self._parse_FROM(l)
                    if m:
                        froms[image_name].append(m['image'])
                        # Register images not yet known
                        if m['image'] not in froms:
                            froms[m['image']] = [None]

            deps = set(froms[image_name])
            self.log.debug('%s dependenc%s: %s' % (
                image_name,
                'y' if (len(deps) == 1) else 'ies',
                ', '.join(deps)
            ))

        tree = {}

        def build_tree(tree, parent, froms):
            childs = [p for (p, v) in froms.items()
                      if parent in v]
            for child in childs:
                tree[child] = {}
                build_tree(tree[child], child, froms)

        build_tree(tree, None, froms)
        self.log.debug(tree)
        self.deps_tree = tree
        return tree

    def gen_staged_deps(self):

        def flatten(stages, depth, deps):
            depth = depth + 1

            stages[depth].extend(deps.keys())
            stages[depth] = sorted(set(stages[depth]))

            for sub_deps in deps.values():
                if sub_deps:
                    flatten(stages, depth, sub_deps)

        stages = defaultdict(list)
        flatten(stages, 0, self.deps_tree)

        for (num, images) in stages.items():
            self.log.debug('Stage %s: %s' % (num, ', '.join(images)))
        self.stages = stages

    def _parse_FROM(self, line):
        # https://docs.docker.com/engine/reference/builder/#from
        m = re.match(
            '''FROM\s+
                (?P<image>\S+?)
                (
                    :(?P<tag>\S+)
                    |
                    @(?P<digest>\S+)
                )?
                (?:\s+as\s+.+)?
                \n$
            ''',
            line, re.X + re.I)
        if m:
            return m.groupdict()

    def build(self, dockerfile):
        self.log.debug('Building %s' % dockerfile)
        image_dir = os.path.dirname(dockerfile)

        image_name = os.path.relpath(image_dir, BASE_DIR)
        self.log.info('Image name: %s' % image_name)

        img = '/'.join([DOCKER_HUB_ACCOUNT, image_name])
        tagged_img = ':'.join([img, DOCKER_TAG_DATE])

        try:
            if os.path.exists(os.path.join(image_dir, 'prebuild.sh')):
                self.log.info("Prebuild script")
                subprocess.check_call(['bash', 'prebuild.sh'], cwd=image_dir)

            cmd = ['docker', 'build']
            if self.config.get('DEFAULT', 'http_proxy'):
                cmd.extend([
                    '--build-arg',
                    'http_proxy=%s' % self.config.get('DEFAULT', 'http_proxy')
                    ])
            cmd.extend(['-t', tagged_img, os.path.dirname(dockerfile)])
            self.log.info(' '.join(cmd))
            subprocess.check_call(cmd)

            cmd = ['docker', 'tag', tagged_img, '%s:latest' % img]
            self.log.info(' '.join(cmd))
            subprocess.check_call(cmd)
        finally:
            for f in glob(os.path.join(image_dir, ".cache-buster*")):
                os.remove(f)

        return True


if __name__ == '__main__':
    builder = DockerBuilder()
    if not builder.run():
        sys.exit(1)
