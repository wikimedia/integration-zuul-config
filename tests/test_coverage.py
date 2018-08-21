#!/usr/bin/env python2
"""
Checks repository coverage, specifically that we cover
all MediaWiki extensions and repositories

Runs daily on Wikimedia Jenkins:
    https://integration.wikimedia.org/ci/job/integration-config-qa/
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

    def __str__(self):
        return "<gerrit active repos>"


class ZuulProjects(list):
    def __repr__(self):
        return "<zuul projects>"

    def __str__(self):
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
        projects = yaml.safe_load(f)['projects']
    return projects


def setup():
    global GERRIT_REPOS
    global ZUUL_PROJECTS
    # Make them custom dict and list that hide __repr__(). See note above
    GERRIT_REPOS = GerritRepos(getGerritRepos())
    project_names = [p['name'] for p in getZuulLayoutProjects()]
    ZUUL_PROJECTS = ZuulProjects(project_names)


test = unittest.TestCase('__init__')
qa = True  # attribute for nose filtering


@attr('qa')
def test_repo_in_zuul():
    repos = [repo for (repo, state) in GERRIT_REPOS.iteritems()
             if repo.startswith(('mediawiki/extensions', 'mediawiki/skins'))
             and len(repo.split('/')) == 3  # skip sub repos
             and state == 'ACTIVE']
    for repo in sorted(repos):
        test.assertIn.__func__.description = (
            'Mediawiki repo is in Zuul: %s' % repo)
        yield test.assertIn, repo, ZUUL_PROJECTS
    del(test.assertIn.__func__.description)


@attr('qa')
def test_zuul_projects_are_in_gerrit():
    """All projects in Zuul layout.yaml must be active in Gerrit"""
    for zuul_project in sorted(ZUUL_PROJECTS):
        test.assertIn.__func__.description = (
            "Zuul project is in Gerrit: %s" % zuul_project)
        yield test.assertIn, zuul_project, GERRIT_REPOS
    del(test.assertIn.__func__.description)


@attr('qa')
def test_gerrit_active_projects_are_in_zuul():
    """All Gerrit active projects are in Zuul layout.yaml"""
    gerrit_active = [
        repo for (repo, state) in GERRIT_REPOS.iteritems()
        if state == 'ACTIVE'
        and repo not in GERRIT_IGNORE
    ]
    for gerrit_project in sorted(gerrit_active):
        test.assertIn.__func__.description = (
            "Gerrit project is in Zuul: %s" % gerrit_project)
        yield test.assertIn, gerrit_project, ZUUL_PROJECTS
    del(test.assertIn.__func__.description)


@attr('qa')
def test_mediawiki_repos_use_quibble():
    for project in getZuulLayoutProjects():
        name = project['name']
        if (
            not name.startswith('mediawiki/extensions')
            or len(name.split('/')) != 3
        ):
            continue
        templates = [t['name'] for t in project['template']]

        if templates == ['archived']:
            continue

        if 'extension-broken' in templates:
            # They do not run Quibble jobs at all on purpose.
            continue

        has_quibble = (
            'extension-gate' in templates
            or 'extension-quibble' in templates
            or 'extension-quibble-composer' in templates
            or 'extension-quibble-noselenium' in templates
            or 'extension-quibble-composer-noselenium' in templates)
        test.assertIn.__func__.description = (
            'MediaWiki extension uses Quibble: %s' % name)
        yield test.assertTrue, has_quibble, \
            'Quibble template not found for %s' % name
