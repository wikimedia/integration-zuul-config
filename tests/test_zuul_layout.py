# Parse Zuul layout.yaml file
#
# Copyright (c) 2016 - Antoine "hashar" Musso
# Copyright (c) 2016 - Wikimedia Foundation Inc.

import os
import unittest

import yaml


class TestZuulLayout(unittest.TestCase):

    layout = None

    @classmethod
    def setUpClass(cls):
        wmf_zuul_layout = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../zuul/layout.yaml')
        with open(wmf_zuul_layout, 'r') as f:
            cls.layout = yaml.load(f)

    def test_mwext_legacy_jslint_replaced_by_npm(self):
        exts = sorted([
            p['name']
            for p in self.layout['projects']
            if p['name'].startswith('mediawiki/extensions/')
            and {'name': 'npm'} in p.get('template', [])
            and {'name': 'extension-jslint'} in p.get('template', [])
            ])

        self.maxDiff = None
        self.longMessage = True
        self.assertListEqual(
            [], exts,
            'MediaWiki extensions having npm do not need "extension-jslint"')
