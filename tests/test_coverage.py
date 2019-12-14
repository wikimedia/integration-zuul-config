#!/usr/bin/env python2
"""
Checks repository coverage, specifically that we cover
all MediaWiki extensions and repositories

Runs daily on Wikimedia Jenkins:
    https://integration.wikimedia.org/ci/job/integration-config-qa/
"""

import json
import os
import urllib
import yaml

import pytest

GERRIT_IGNORE = (
    'All-Avatars',
    'All-Users',
    'analytics/aggregator/data',
    'analytics/aggregator/projectview/data',
    'analytics/limn-analytics-data',
    'analytics/limn-edit-data',
    'analytics/limn-ee-data',
    'analytics/limn-extdist-data',
    'analytics/limn-flow-data',
    'analytics/limn-multimedia-data',
    'labs/maps',
    'operations/debs',
    'sandbox',
    'wikimedia/annualreport',
    'wikimedia/education',
    'wikimedia/endowment',  # empty
    'wikimedia/security',
    'wiktionary/anagrimes',  # some legacy perl
)

# Dummy classes to hide dict/list representation.
#
# nose.plugins.xunit describes the tests and expands its arguments, the Gerrit
# and Zuul projects ends up being appended to each testcase which causes a huge
# xml file.
# Hidding the actual content by overriding __repr__ and __str__ ensure we have
# a manageable file size.


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


@pytest.fixture(scope='module')
def gerrit_repos():
    req = urllib.urlopen(
        'https://gerrit.wikimedia.org/r/projects/?type=code&description')
    # Strip Gerrit json harness: )]}'
    req.readline()
    return GerritRepos({
        name: meta['state']
        for (name, meta) in json.load(req).iteritems()
    })


def getZuulLayoutProjects():
    layout = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '../zuul/layout.yaml')
    with open(layout) as f:
        projects = yaml.safe_load(f)['projects']
    return projects


@pytest.fixture(scope='module')
def zuul_projects():
    project_names = [p['name'] for p in getZuulLayoutProjects()]
    return ZuulProjects(sorted(project_names))


@pytest.mark.qa
def test_repo_in_zuul(gerrit_repos, zuul_projects):
    repos = [repo for (repo, state) in gerrit_repos.iteritems()
             if repo.startswith(('mediawiki/extensions', 'mediawiki/skins'))
             and len(repo.split('/')) == 3  # skip sub repos
             and state == 'ACTIVE']
    for repo in sorted(repos):
        assert repo in zuul_projects, 'Mediawiki repo is in Zuul: %s' % repo


@pytest.mark.qa
def test_zuul_projects_are_in_gerrit(zuul_projects, gerrit_repos):
    """All projects in Zuul layout.yaml must be active in Gerrit"""
    for zuul_project in sorted(zuul_projects):
        assert zuul_project in gerrit_repos, \
            "Zuul project is in Gerrit: %s" % zuul_project


@pytest.mark.qa
def test_gerrit_active_projects_are_in_zuul(gerrit_repos, zuul_projects):
    """All Gerrit active projects are in Zuul layout.yaml"""
    gerrit_active = [
        repo for (repo, state) in gerrit_repos.iteritems()
        if state == 'ACTIVE'
        and repo not in GERRIT_IGNORE
    ]
    for gerrit_project in sorted(gerrit_active):
        assert gerrit_project in zuul_projects, \
            "Gerrit project is in Zuul: %s" % gerrit_project


@pytest.mark.qa
def test_mediawiki_repos_use_quibble():
    for project in getZuulLayoutProjects():
        name = project['name']
        if name == 'mediawiki/extensions/DonationInterface':
            # Does not use any Quibble template but a specific job
            continue

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
        assert has_quibble is True, \
            'Quibble template not found for %s' % name


@pytest.mark.qa
def test_repos_with_debian_files_have_debian_glue_job():

    def has_debian_glue(zuul_project_def):
        for template in zuul_project_def.get('template', []):
            if template['name'].startswith('debian-glue'):
                return True

        for (k, v) in zuul_project_def.iteritems():
            if k == 'name' or k == 'template':
                continue
            has_job = any([job for job in v if job.startswith('debian-glue')])
            if has_job:
                return True

    debian_glued = sorted([
        project['name']
        for project in getZuulLayoutProjects()
        if has_debian_glue(project)])

    req = urllib.urlopen('https://gerrit.wikimedia.org/r/changes/?'
                         'q=file:^debian/.*+-age:6months')
    # Strip gerrit json harness
    req.readline()

    debian_projects = sorted(list(set(
        [change['project'] for change in json.load(req)]
    )))
    for d in debian_projects:
        assert d in debian_glued, \
            'Repository with debian changes but no debian glue job: %s' % d
