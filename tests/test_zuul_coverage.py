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


class TestZuulCoverage(unittest.TestCase):

    maxDiff = None

    def getExtDistRepos(self):
        req = urllib.urlopen(
            'https://www.mediawiki.org/w/api.php?action=query'
            '&list=extdistrepos&format=json&continue'
        )
        data = json.load(req)
        req.close()
        return data['query']['extdistrepos']

    def getLayoutProjects(self):
        layout = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../zuul/layout.yaml')
        with open(layout) as f:
            projects = [p['name'] for p in yaml.safe_load(f)['projects']]
        return projects

    def test_all_extensions_have_gate_and_submit(self):
        projects = self.getLayoutProjects()
        extensions = self.getExtDistRepos()['extensions']
        missing = []
        for extension in extensions:
            if 'mediawiki/extensions/%s' % extension not in projects:
                missing.append(extension)
        self.assertEqual([], missing)

    def test_all_skins_have_gate_and_submit(self):
        projects = self.getLayoutProjects()
        skins = self.getExtDistRepos()['skins']
        missing = []
        for skin in skins:
            if 'mediawiki/skins/%s' % skin not in projects:
                missing.append(skin)
        self.assertEqual([], missing)
