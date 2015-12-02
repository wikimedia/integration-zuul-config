import json
import os.path
import unittest
import urllib2

import yaml

CFG_URL = 'https://phabricator.wikimedia.org/diffusion/MREL/browse/master/make-wmf-branch/config.json?view=raw'  # noqa
ZUUL_LAYOUT = os.path.join(os.path.dirname(__file__), '../zuul/layout.yaml')


def get_make_wmf_branch_config():
    request = urllib2.urlopen(CFG_URL)
    return json.load(request)

CFG = get_make_wmf_branch_config()

class TestWikimediaRepos(unittest.TestCase):

    zuul_projects = None
    wmf_exts = None
    wmf_skins = None

    @classmethod
    def setUpClass(cls):
        with open(ZUUL_LAYOUT) as f:
            layout = yaml.load(f)
        cls.zuul_projects = {p.get('name'): p for p in layout.get('projects')}

        cls.wmf_exts = {
            'mediawiki/extensions/%s' % e
            for e in CFG['extensions'] + CFG['special_extensions'].keys()}
        cls.wmf_skins = {'mediawiki/skins/%s' % e for e in CFG['skins']}

    def test_wmf_repos_in_zuul(self):
        projects_in_zuul = set(self.zuul_projects.keys())
        self.longMessage = True
        self.assertEqual(set(), self.wmf_exts - projects_in_zuul,
                         'WMF deployed extensions must be in Zuul')
        self.assertEqual(set(), self.wmf_skins - projects_in_zuul,
                         'WMF deployed skins must be in Zuul')

    def test_wmf_skins_ci_config(self):
        for wmf_skin in self.wmf_skins:
            zuul_conf = self.zuul_projects[wmf_skin]
            templates = [t.get('name') for t in zuul_conf.get('template')]
            self.assertIn('npm', templates, 'Skins must have npm')

    def test_wmf_extensions_ci_config(self):
        issues = []
        requirements = ['npm', 'jshint']
        for wmf_extension in sorted(self.wmf_exts):
            zuul_conf = self.zuul_projects[wmf_extension]
            repo_templates = sorted([t.get('name') for t in zuul_conf.get('template')])

            try:
                self.assertGreaterEqual(requirements, repo_templates)
                #self.assertLessEqual(
                #    requirements, repo_templates,
                #    '%s must have Zuul template npm (has: %s)' % (
                #        wmf_extension, ', '.join(repo_templates)))
            except AssertionError, e:
                issues.append(e.message)
        self.maxDiff = None
        self.assertMultiLineEqual('', '\n'.join(issues))
