#!/usr/bin/env python3

import argparse
from collections import defaultdict
import configparser
from datetime import datetime
from glob import glob
import logging
import os
import re
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JJB_DIR = os.path.join(os.path.dirname(BASE_DIR), 'jjb')
DOCKER_TAG_DATE = datetime.utcnow().strftime("v%Y.%m.%d.%H.%M")
DOCKER_HUB_ACCOUNT = 'wmfreleng'


class DockerBuilder(object):

    def __init__(self, base_dir=BASE_DIR):
        self.base_dir = base_dir
        self.pushes = []

    def run(self):
        self.parse_args()

        self.log = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=self.args.verbose)

        self.load_config()

        recurse = self.args.recurse

        if self.args.directory:
            to_build = self.args.directory
        else:
            # Base images
            to_build = ['ci-jessie', 'ci-stretch']
            # No images provided, so we're building all of them.
            recurse = True

        if recurse:
            deps_tree = self.gen_deps_tree()

        images = []
        for image in to_build:
            images.append(image)
            if recurse:
                tree = DockerBuilder.find_subtree(
                    deps_tree,
                    DOCKER_HUB_ACCOUNT + '/' + image)
                # Extend build list to sub-images.
                # Note that we need to strip the "wmfreleng/" prefix
                images.extend([x.split('/')[1]
                               for x in self.gen_staged_deps(tree)])

        self.log.info('Will build: %s' % ', '.join(images))
        dockerfiles = [
            os.path.join(self.base_dir, f, 'Dockerfile')
            for f in images
        ]

        if not all(map(self.build, dockerfiles)):
            return False

        self.log.info('You can push the following images when ready: %s'
                      % ' && '.join('docker push %s'
                                    % name for name in self.pushes))

    def load_config(self):
        config = configparser.ConfigParser()
        config.read([
            os.path.join(self.base_dir, 'build.conf.default'),
            os.path.join(self.base_dir, 'build.conf'),
        ])
        self.config = config

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('directory', nargs='*', default=[])
        parser.add_argument(
            '-v', '--verbose', action='store_const',
            const=logging.DEBUG, default=logging.INFO)
        parser.add_argument(
            '-n', '--dry-run', action='store_true',
            help='Do not run commands')
        parser.add_argument(
            '--no-cache', action='store_true',
            help='Do not use cache when building the image'
        )
        parser.add_argument(
            '--run-tests', action='store_true',
            help='Run tests in example-run.sh if it exists after building'
        )
        parser.add_argument(
            '--update-jjb', action='store_true',
            help='Update tags in jjb yaml files'
        )
        parser.add_argument(
            '--recurse', action='store_true',
            help='Rebuild images that depend on this one'
        )
        self.args = parser.parse_args()

    def find_docker_files(self):
        return sorted(glob(os.path.join(self.base_dir, '*/Dockerfile')))

    def update_jjb(self, img, tagged_img):
        regex = re.compile('%s:v[0-9\.]+' % img)
        for fname in os.listdir(JJB_DIR):
            if not fname.endswith('.yaml'):
                continue
            full_fname = os.path.join(JJB_DIR, fname)
            with open(full_fname, 'r') as f:
                text = f.read()
            if regex.search(text):
                new_text = regex.sub(tagged_img, text)
                with open(full_fname, 'w') as f:
                    f.write(new_text)
                self.log.info('Updated %s' % full_fname)

    def gen_deps_tree(self):
        return DockerBuilder.build_tree(
            self.find_from())

    def find_from(self):
        froms = {}
        for f in self.find_docker_files():
            image_name = '%s/%s' % (DOCKER_HUB_ACCOUNT,
                                    os.path.basename(os.path.dirname(f)))
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
        return froms

    @staticmethod
    def build_tree(froms):
        tree = {}

        def build_tree(tree, parent, froms):
            childs = [p for (p, v) in froms.items()
                      if parent in v]
            for child in childs:
                tree[child] = {}
                build_tree(tree[child], child, froms)

        build_tree(tree, None, froms)
        return tree

    @staticmethod
    def find_subtree(tree, root):
        if root in tree:
            return tree[root]

        for subtree in tree.values():
            found = DockerBuilder.find_subtree(subtree, root)
            if found is not None:
                return found

        return None

    def gen_staged_deps(self, tree):

        def flatten(stages, depth, deps):
            depth = depth + 1

            stages[depth].extend(deps.keys())
            stages[depth] = sorted(set(stages[depth]))

            for sub_deps in deps.values():
                if sub_deps:
                    flatten(stages, depth, sub_deps)

        stages = defaultdict(list)
        flatten(stages, 0, tree)

        for (num, images) in stages.items():
            self.log.debug('Stage %s: %s' % (num, ', '.join(images)))

        flat = []
        for stage in sorted(stages):
            flat.extend(stages[stage])
        return flat

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

        image_name = os.path.relpath(image_dir, self.base_dir)
        self.log.info('Image name: %s' % image_name)

        img = '/'.join([DOCKER_HUB_ACCOUNT, image_name])
        tagged_img = ':'.join([img, DOCKER_TAG_DATE])

        try:
            if os.path.exists(os.path.join(image_dir, 'prebuild.sh')):
                self.log.info("Prebuild script")
                self.run_cmd(['bash', 'prebuild.sh'], cwd=image_dir)

            cmd = ['docker', 'build']
            if self.config.get('DEFAULT', 'http_proxy'):
                cmd.extend([
                    '--build-arg',
                    'http_proxy=%s' % self.config.get('DEFAULT', 'http_proxy')
                    ])
            if self.args.no_cache:
                cmd.extend(['--no-cache'])
            cmd.extend(['-t', tagged_img, os.path.dirname(dockerfile)])
            self.run_cmd(cmd)

            cmd = ['docker', 'tag', tagged_img, '%s:latest' % img]
            self.run_cmd(cmd)
        finally:
            for f in glob(os.path.join(image_dir, ".cache-buster*")):
                os.remove(f)

        if self.args.run_tests and \
                os.path.exists(os.path.join(image_dir, 'example-run.sh')):
            self.log.info('Running tests')
            self.run_cmd(['bash', 'example-run.sh'], cwd=image_dir)

        self.pushes.append(tagged_img)
        self.pushes.append('%s:latest' % img)

        if self.args.update_jjb:
            self.update_jjb(img, tagged_img)

        return True

    def run_cmd(self, args, **kwargs):
        self.log.info('%s' % (' '.join(args)))
        if not self.args.dry_run:
            subprocess.check_call(args, *kwargs)


if __name__ == '__main__':
    builder = DockerBuilder()
    if not builder.run():
        sys.exit(1)
