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

# Dummy classes to hide dict/list representation.
#
# nose.plugins.xunit describes the tests and expands its arguments, the Gerrit
# and Zuul projects ends up being happened to each testcase which causes a huge
# xml file.
# Hidding the actual content by overriding __repr__ ensure we have a manageable
# file size.


class GerritRepos(dict):
    def __repr__(self):
        return "<gerrit active repos>"


class ZuulProjects(list):
    def __repr__(self):
        return "<zuul projects>"


# Globals, initialized in setup()
GERRIT_REPOS = None
ZUUL_PROJECTS = None


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
    # Make them custom dict and list that hide __repr__(). See note above
    GERRIT_REPOS = GerritRepos(getGerritRepos())
    ZUUL_PROJECTS = ZuulProjects(getZuulLayoutProjects())


test = unittest.TestCase('__init__')
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
    """All projects in Zuul layout.yaml must be active in Gerrit"""
    for zuul_project in sorted(ZUUL_PROJECTS):
        test.assertIn.__func__.description = (
            "Zuul project is in Gerrit: %s" % zuul_project)
        yield test.assertIn, zuul_project, GERRIT_REPOS, (
            '%s is not active in Gerrit' % zuul_project)
    del(test.assertIn.__func__.description)


@attr('qa')
def test_gerrit_active_projects_are_in_zuul():
    """All Gerrit active projects are in Zuul layout.yaml"""
    gerrit_active = set([
        repo for (repo, state) in GERRIT_REPOS.iteritems()
        if state == 'ACTIVE'
        and repo not in GERRIT_IGNORE
    ])
    for gerrit_project in gerrit_active:
        test.assertIn.__func__.description = (
            "Gerrit project is in Zuul: %s" % gerrit_project)
        yield test.assertIn, gerrit_project, ZUUL_PROJECTS, (
            '%s is not configured in Zuul' % gerrit_project)
    del(test.assertIn.__func__.description)
