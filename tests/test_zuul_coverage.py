#!/usr/bin/env python2
"""
Checks repository coverage, specifically that we cover
all MediaWiki extensions and repositories
"""

import json
import os
import unittest
import urllib
import yaml

from nose.plugins.attrib import attr


@attr('qa')
class TestZuulCoverage(unittest.TestCase):

    maxDiff = None
    _repos = None

    @classmethod
    def setUpClass(cls):
        req = urllib.urlopen(
            'https://gerrit.wikimedia.org/r/projects/?type=code&description')
        # Strip Gerrit json harness: )]}'
        req.readline()
        cls._repos = sorted([
            name for (name, meta) in json.load(req).iteritems()
            if meta['state'] == 'ACTIVE'
        ])

    def getLayoutProjects(self):
        layout = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../zuul/layout.yaml')
        with open(layout) as f:
            projects = [p['name'] for p in yaml.safe_load(f)['projects']]
        return projects

    def assert_have_gate_and_submit(self, prefix):
        projects = self.getLayoutProjects()
        missing = [repo for repo in self._repos
                   if repo.startswith(prefix) and repo not in projects]

        self.longMessage = True
        self.assertEqual(
            [], missing,
            '%s %s are not configured in zuul' % (len(missing), prefix))

    def test_all_extensions_have_gate_and_submit(self):
        self.assert_have_gate_and_submit('mediawiki/extensions/')

    def test_all_skins_have_gate_and_submit(self):
        self.assert_have_gate_and_submit('mediawiki/skins/')
