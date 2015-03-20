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
    _extdistrepos = None

    @classmethod
    def setUpClass(cls):
        req = urllib.urlopen(
            'https://www.mediawiki.org/w/api.php?action=query'
            '&list=extdistrepos&format=json&continue'
        )
        data = json.load(req)
        req.close()
        cls._extdistrepos = data['query']['extdistrepos']

    def getExtDistRepos(self):
        return self._extdistrepos

    def getLayoutProjects(self):
        layout = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../zuul/layout.yaml')
        with open(layout) as f:
            projects = [p['name'] for p in yaml.safe_load(f)['projects']]
        return projects

    def assert_have_gate_and_submit(self, kind):
        assert kind in ['extensions', 'skins'], 'Unrecognized: %s' % kind

        projects = self.getLayoutProjects()
        repos = self.getExtDistRepos()[kind]
        missing = []
        for repo in repos:
            if 'mediawiki/%s/%s' % (kind, repo) not in projects:
                missing.append(repo)

        self.longMessage = True
        self.assertEqual(
            [], missing,
            'Some %s are not configured in zuul' % kind)

    def test_all_extensions_have_gate_and_submit(self):
        self.assert_have_gate_and_submit('extensions')

    def test_all_skins_have_gate_and_submit(self):
        self.assert_have_gate_and_submit('skins')
