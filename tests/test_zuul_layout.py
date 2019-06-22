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

    def getExtSkinRepos(self):
        projects = []
        for project in self.layout['projects']:
            if not project['name'].startswith((
                    'mediawiki/skins', 'mediawiki/extensions')):
                continue
            if len(project['name'].split('/')) != 3:
                # Skip sub repositories
                continue
            projects.append(project)

        return projects

    def test_mediawiki_ext_skins_have_test_templates(self):
        one_of_templates = (
            'archived',
            'extension-broken',
            'extension-unittests',
            'extension-quibble',
            'skin-tests',
            'skin-quibble',
            'extension-gate',
            'quibble-vendor',
            )
        errors = []
        for project in self.getExtSkinRepos():
            try:
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

    def test_gated_extensions_have_quibble_regular_template(self):
        errors = []
        for project in self.getExtSkinRepos():
            try:
                if 'template' not in project:
                    continue

                templates = [template['name']
                             for template in project.get('template')]
                if 'extension-gate' not in templates:
                    continue

                # Extract singular 'extension' or 'skin'
                kind = project['name'].split('/')[1][:-1]

                self.assertIn(
                    '%s-quibble' % kind,
                    templates,
                    'Must have "%s-quibble": %s' % (kind, project['name'])
                )

            except AssertionError, e:
                errors.append(str(e))

        self.maxDiff = None
        self.assertListEqual([], errors)

    def test_bluespice_repos_use_composer_template(self):
        errors = []
        bsrepos = [r for r in self.getExtSkinRepos()
                   if '/BlueSpice' in r['name']]
        for project in bsrepos:
            try:
                if 'template' not in project:
                    continue
                templates = [template['name']
                             for template in project.get('template')]

                # Extract singular 'extension' or 'skin'
                kind = project['name'].split('/')[1][:-1]

                required = [
                    '%s-broken' % kind,
                    '%s-quibble-composer-noselenium' % kind,
                    '%s-quibble-composer' % kind,
                    ]
                self.assertTrue(
                    any([r in templates for r in required]),
                    '%s must have one of [%s]. Got: %s' % (
                        project['name'],
                        ', '.join(required),
                        ', '.join(templates),
                    )
                )
            except AssertionError, e:
                errors.append(str(e))

        self.maxDiff = None
        self.assertListEqual([], errors)
