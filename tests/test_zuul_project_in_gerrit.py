import json
import os
import urllib2

from nose.plugins.attrib import attr
import yaml

GERRIT_URL = 'https://gerrit.wikimedia.org/r/projects/?type=code'
ZUUL_LAYOUT = os.path.join(os.path.dirname(__file__), '../zuul/layout.yaml')


def get_gerrit_repos():
    """
    Connect to gerrit.wikimedia.org to retrieve a list of public projects.

    Returns a sorted list of project names
    """
    request = urllib2.urlopen(GERRIT_URL)
    # Strip Gerrit json harness: )]}'
    request.readline()
    projects = json.load(request)
    return sorted(projects.keys())


GERRIT_REPOS = get_gerrit_repos()


@attr('qa')
def test_zuul_project_in_gerrit():

    with open(ZUUL_LAYOUT) as f:
        layout = yaml.load(f)
    for pj in layout.get('projects'):
        yield is_in_gerrit, pj.get('name')


def is_in_gerrit(zuul_project):
    msg = "Project configured in Zuul is not in Gerrit: %s" % (zuul_project)
    assert zuul_project in GERRIT_REPOS, msg
