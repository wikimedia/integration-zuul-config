import json
import os.path
import unittest
import urllib2

import yaml

CFG_URL = 'https://phabricator.wikimedia.org/diffusion/MREL/browse/master/make-wmf-branch/config.json?view=raw'  # noqa
CONFIG_SOURCE = os.environ.get('MAKE_WMF_BRANCH_CONFIG') or CFG_URL
ZUUL_LAYOUT = os.path.join(os.path.dirname(__file__), '../zuul/layout.yaml')


def get_make_wmf_branch_config(source):
    '''
    Load mediawiki/tools/release make-wmf-branch/config.json

    @param source: http URL or path to file
    '''
    if source.startswith('http'):
        request = urllib2.urlopen(source)
        return json.load(request)
    else:
        with open(source, 'r') as f:
            return json.load(f)

CFG = get_make_wmf_branch_config(source=CONFIG_SOURCE)


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

    def test_wmf_extensions_in_zuul(self):
        "WMF deployed extensions are in Zuul"
        projects_in_zuul = set(self.zuul_projects.keys())
        self.maxDiff = None
        self.assertMultiLineEqual(
            '\n'.join(self.wmf_exts - projects_in_zuul), '')

    def test_wmf_skins_in_zuul(self):
        "WMF deployed skins are in Zuul"
        projects_in_zuul = set(self.zuul_projects.keys())
        self.longMessage = True
        self.assertEqual(set(), self.wmf_skins - projects_in_zuul,
                         'WMF deployed skins must be in Zuul')

    def test_wmf_skins_ci_config(self):
        "WMF deployed skins have proper Zuul templates"
        errors = []
        for wmf_skin in self.wmf_skins:
            try:
                zuul_conf = self.zuul_projects[wmf_skin]
                templates = [t.get('name') for t in zuul_conf.get('template')]
                self.assertIn('npm', templates,
                              'WMF deployed skin %s must have npm' % wmf_skin)
            except AssertionError, e:
                errors.append(e)
        self.assertListEqual([], errors)

    def test_wmf_repos_ci_config(self):
        "WMF deployed repos have proper Zuul templates"
        errors = []
        requirements = {'npm'}
        for wmf_repo in sorted(self.wmf_exts | self.wmf_skins):
            if wmf_repo not in self.zuul_projects:
                # Covered by: test_wmf_extensions_in_zuul
                #             test_wmf_skins_in_zuul
                continue

            zuul_conf = self.zuul_projects[wmf_repo]
            repo_templates = set([t.get('name')
                                  for t in zuul_conf.get('template')])

            try:
                missing = requirements - repo_templates
                msg = '%s miss Zuul template(s): %s' % (
                    wmf_repo, ', '.join(missing))
                self.assertSetEqual(set(), missing, msg)

            except AssertionError, e:
                errors.append(e.message)
        self.maxDiff = None
        self.assertMultiLineEqual('', '\n'.join(errors))
