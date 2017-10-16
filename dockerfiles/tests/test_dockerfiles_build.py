import logging
import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, '..'))

import build


FIXTURES = os.path.join(BASE_DIR, 'fixtures', 'dockerfiles')


class TestDockerfilesBuild(unittest.TestCase):

    deps_tree = None

    @classmethod
    def setUpClass(cls):
        b = build.DockerBuilder(base_dir=FIXTURES)
        b.log = logging.getLogger()
        cls.deps_tree = b.gen_deps_tree()

    @staticmethod
    def image_deps(image):
        return build.DockerBuilder.find_subtree(
            TestDockerfilesBuild.deps_tree,
            TestDockerfilesBuild.make_image_name(image)
            )

    @staticmethod
    def make_image_name(name):
        return os.path.join(build.DOCKER_HUB_ACCOUNT, name)

    def test_parse_from(self):
        b = build.DockerBuilder(base_dir=FIXTURES)
        x = b._parse_FROM('FROM foo:1.2.3 as bar')
        self.assertTrue(x['image'] == 'foo')
        self.assertTrue(x['tag'] == '1.2.3')
        self.assertTrue(x['digest'] is None)

    def test_find_docker_files(self):
        b = build.DockerBuilder(base_dir=FIXTURES)
        docker_files = b.find_docker_files()
        base_file = os.path.join(FIXTURES, 'ci-fixture', 'Dockerfile')
        self.assertTrue(len(docker_files) > 0)
        self.assertTrue(base_file in docker_files)

    def test_gen_deps_tree_three_depends_on_two(self):
        base_tree = TestDockerfilesBuild.image_deps('ci-fixture-child-two')
        self.assertTrue(base_tree is not None)
        self.assertTrue(
            self.make_image_name('ci-fixture-child-three') in base_tree.keys())

    def test_gen_deps_tree_two_depends_on_base(self):
        base_tree = TestDockerfilesBuild.image_deps('ci-fixture')
        self.assertTrue(base_tree is not None)
        two = base_tree.get(self.make_image_name('ci-fixture-child-two'))
        self.assertTrue(two is not None)
        self.assertTrue(
            two[self.make_image_name('ci-fixture-child-three')] is not None)
