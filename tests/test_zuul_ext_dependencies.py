import os
import unittest

from fakes import FakeJob

dependencies = {}  # defined for flake8
set_ext_dependencies = None  # defined for flake8
# Import function
execfile(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../zuul/ext_dependencies.py'))


class TestExtDependencies(unittest.TestCase):
    def assertHasDependencies(self, params):
        self.assertIn('EXT_DEPENDENCIES', params)

    def assertMissingDependencies(self, params):
        self.assertNotIn('EXT_DEPENDENCIES', params)

    def fetch_dependencies(self, job_name=None, project=None):
        if project:
            params = {'ZUUL_PROJECT': project}
        else:
            params = {'ZUUL_PROJECT': 'mediawiki/extensions/Example'}
        job = FakeJob(job_name if job_name else 'mwext-testextension-hhvm')
        set_ext_dependencies(None, job, params)
        return params

    def test_ext_name(self):
        params = self.fetch_dependencies(
            project='mediawiki/extensions/Example')

        self.assertIn('EXT_NAME', params)
        self.assertEqual(params['EXT_NAME'], 'Example')

    def test_resolvable_dependencies(self):
        """verifies that we can resolve all of the dependencies"""
        for ext_name in dependencies:
            self.assertHasDependencies(self.fetch_dependencies(
                project='mediawiki/extensions/' + ext_name))

    def test_job_name(self):
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwext-testextension-hhvm'))
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwext-qunit'))
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwext-mw-selenium'))
        self.assertMissingDependencies(self.fetch_dependencies(
            job_name='mediawiki-core-phplint'))

    def test_zuul_project_name(self):
        self.assertHasDependencies(self.fetch_dependencies(
            project='mediawiki/extensions/Example'))
        self.assertMissingDependencies(self.fetch_dependencies(
            project='mediawiki/extensions'))
        self.assertMissingDependencies(self.fetch_dependencies(
            project='mediawiki/extensions/Example/vendor'))
        self.assertMissingDependencies(self.fetch_dependencies(
            project='foo/bar/baz'))
