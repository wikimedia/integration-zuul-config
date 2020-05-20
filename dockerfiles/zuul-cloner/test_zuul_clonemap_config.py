# Verify Wikimedia zuul-cloner clonemap
#
# Copyright (c) 2014 - Antoine "hashar" Musso
# Copyright (c) 2014 - Wikimedia Foundation Inc.

import os
import unittest

import yaml
from zuul.lib.clonemapper import CloneMapper


class TestZuulClonemap(unittest.TestCase):

    yaml_conf = None
    TEST_ROOT = '/test-root'

    def __init__(self, *args, **kwargs):
        super(TestZuulClonemap, self).__init__(*args, **kwargs)
        clonemap_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            './zuul-clonemap.yaml')
        with open(clonemap_file, 'r') as content:
            self.yaml_conf = content.read()

    def getProjectMap(self, project):
        cm = CloneMapper(yaml.safe_load(self.yaml_conf).get('clonemap'),
                         [project])
        return cm.expand(self.TEST_ROOT)

    def test_conf_is_valid_yaml(self):
        conf = yaml.safe_load(self.yaml_conf)
        self.assertIn('clonemap', conf)

    def test_expand_mediawiki_core_to_root(self):
        mapping = self.getProjectMap('mediawiki/core')
        self.assertIn('mediawiki/core', mapping)
        self.assertEquals(self.TEST_ROOT, mapping.get('mediawiki/core'))

    def test_expand_mediawiki_vendor_to_vendor(self):
        mapping = self.getProjectMap('mediawiki/vendor')
        self.assertIn('mediawiki/vendor', mapping)
        self.assertEquals(os.path.join(self.TEST_ROOT, 'vendor'),
                          mapping.get('mediawiki/vendor'))

    def test_expand_mediawiki_extensions_under_extensions(self):
        mapping = self.getProjectMap('mediawiki/extensions/Foobar')
        self.assertEquals(os.path.join(self.TEST_ROOT, 'extensions/Foobar'),
                          mapping.get('mediawiki/extensions/Foobar'))

    def test_expand_mediawiki_skins_under_skins(self):
        mapping = self.getProjectMap('mediawiki/skins/Vector')
        self.assertEquals(os.path.join(self.TEST_ROOT, 'skins/Vector'),
                          mapping.get('mediawiki/skins/Vector'))
