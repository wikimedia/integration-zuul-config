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
    'sandbox',
    'wikibase',
    'wikimedia/annualreport',
    'wikimedia/education',
    'wikimedia/endowment',  # empty
    'wikimedia/security',
    'wikipedia',
    'wikipedia/gadgets',
    'wiktionary/anagrimes',  # some legacy perl
)

GERRIT_REPOS = {}
ZUUL_PROJECTS = []


def getGerritRepos():
    req = urllib.urlopen(
        'https://gerrit.wikimedia.org/r/projects/?type=code&description')
    # Strip Gerrit json harness: )]}'
    req.readline()
    return {
        name: meta['state']
        for (name, meta) in json.load(req).iteritems()
    }


def getZuulLayoutProjects():
    layout = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '../zuul/layout.yaml')
    with open(layout) as f:
        projects = [p['name'] for p in yaml.safe_load(f)['projects']]
    return projects


def setup():
    global GERRIT_REPOS
    global ZUUL_PROJECTS
    GERRIT_REPOS = getGerritRepos()
    ZUUL_PROJECTS = getZuulLayoutProjects()

test = unittest.TestCase('__init__')
test.maxDiff = None
test.longMessage = True
qa = True  # attribute for nose filtering


def assert_have_gate_and_submit(prefix):
    missing = [repo for (repo, state) in GERRIT_REPOS.iteritems()
               if repo.startswith(prefix)
               and len(repo.split('/')) == 3  # skip sub repos
               and state == 'ACTIVE'
               and repo not in ZUUL_PROJECTS]
    test.assertEqual(
        [], sorted(missing),
        '%s %s are not configured in zuul' % (len(missing), prefix))


@attr('qa')
def test_all_extensions_have_gate_and_submit():
    assert_have_gate_and_submit('mediawiki/extensions/')


@attr('qa')
def test_all_skins_have_gate_and_submit():
    assert_have_gate_and_submit('mediawiki/skins/')


@attr('qa')
def test_zuul_projects_are_in_gerrit():
    zuul = set(ZUUL_PROJECTS)
    gerrit = set(GERRIT_REPOS)
    test.assertEqual(
        [], sorted((zuul & gerrit) ^ zuul),
        'Projects configured in Zuul but no more active in Gerrit')


@attr('qa')
def test_gerrit_active_projects_are_in_zuul():
    zuul = set(ZUUL_PROJECTS)
    gerrit_active = set([
        repo for (repo, state) in GERRIT_REPOS.iteritems()
        if state == 'ACTIVE'
        and repo not in GERRIT_IGNORE
    ])
    test.assertEqual(
        [], sorted((zuul & gerrit_active) ^ gerrit_active),
        'Projects in Gerrit are all configured in Gerrit')
