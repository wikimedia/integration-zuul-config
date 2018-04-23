# Parse Zuul layout.yaml file
#
# Copyright (c) 2016 - Antoine "hashar" Musso
# Copyright (c) 2016 - Wikimedia Foundation Inc.

import os
import unittest

import yaml


class TestZuulLayout(unittest.TestCase):
    """
    Tests solely asserting on the Zuul YAML configuration.

    Notably expansion of templates are not available which is provied by the
    scheduler and tested via test_zuul_scheduler.py
    """

    layout = None

    @classmethod
    def setUpClass(cls):
        wmf_zuul_layout = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../zuul/layout.yaml')
        with open(wmf_zuul_layout, 'r') as f:
            cls.layout = yaml.load(f)

    def test_mediawiki_ext_skins_have_test_templates(self):
        one_of_templates = (
            'archived',
            'extension-unittests',
            'skin-tests',
            'extension-gate',
            'quibble-vendor',
            )
        errors = []
        for project in self.layout['projects']:
            try:
                if not project['name'].startswith((
                        'mediawiki/skins', 'mediawiki/extensions')):
                    continue

                if len(project['name'].split('/')) != 3:
                    # Skip sub repositories
                    continue

                has_extension_unittests = any([
                    template['name'].startswith(one_of_templates)
                    for template in project.get('template', {})
                    ])
                self.assertTrue(
                    has_extension_unittests,
                    'Project %s in Zuul lacks an extension-unittests* '
                    'template' % project['name'])
            except AssertionError, e:
                errors.append(str(e))

        self.maxDiff = None
        self.assertListEqual([], errors)
