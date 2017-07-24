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

GERRIT_IGNORE = (
    'All-Users',
    'analytics/aggregator/data',
    'analytics/aggregator/projectview/data',
    'analytics/limn-analytics-data',
    'analytics/limn-edit-data',
    'analytics/limn-ee-data',
    'analytics/limn-extdist-data',
    'analytics/limn-flow-data',
    'analytics/limn-multimedia-data',
    'labs',
    'labs/maps',
    'mediawiki/libs',
    'operations/debs',
    'wikibase',
    'wikimedia/education',
    'wikimedia/security',
    'wikipedia',
)


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
        cls._repos = {
            name: meta['state']
            for (name, meta) in json.load(req).iteritems()
        }

    def getLayoutProjects(self):
        layout = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../zuul/layout.yaml')
        with open(layout) as f:
            projects = [p['name'] for p in yaml.safe_load(f)['projects']]
        return projects

    def assert_have_gate_and_submit(self, prefix):
        projects = self.getLayoutProjects()
        missing = [repo for (repo, state) in self._repos.iteritems()
                   if repo.startswith(prefix)
                   and len(repo.split('/')) == 3  # skip sub repos
                   and state == 'ACTIVE'
                   and repo not in projects]

        self.longMessage = True
        self.assertEqual(
            [], sorted(missing),
            '%s %s are not configured in zuul' % (len(missing), prefix))

    def test_all_extensions_have_gate_and_submit(self):
        self.assert_have_gate_and_submit('mediawiki/extensions/')

    def test_all_skins_have_gate_and_submit(self):
        self.assert_have_gate_and_submit('mediawiki/skins/')

    def test_zuul_projects_are_in_gerrit(self):
        zuul = set(self.getLayoutProjects())
        gerrit = set(self._repos.keys())
        self.longMessage = True
        self.assertEqual(
            [], sorted((zuul & gerrit) ^ zuul),
            'Projects configured in Zuul but no more active in Gerrit')

    def test_gerrit_active_projects_are_in_zuul(self):
        zuul = set(self.getLayoutProjects())
        gerrit_active = set([
            repo for (repo, state) in self._repos.iteritems()
            if state == 'ACTIVE'
            and repo not in GERRIT_IGNORE
        ])
        self.longMessage = True
        self.assertEqual(
            [], sorted((zuul & gerrit_active) ^ gerrit_active),
            'Projects in Gerrit are all configured in Gerrit')
