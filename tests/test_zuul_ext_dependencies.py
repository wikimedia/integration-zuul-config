import os
import unittest

from fakes import FakeJob

dependencies = {}  # defined for flake8
get_dependencies = None  # defined for flake8
set_parameters = None  # defined for flake8
# Import function
execfile(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../zuul/parameter_functions.py'))


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
        set_parameters(None, job, params)
        return params

    def test_ext_name(self):
        params = self.fetch_dependencies(
            project='mediawiki/extensions/Example')

        self.assertIn('EXT_NAME', params)
        self.assertEqual(params['EXT_NAME'], 'Example')

    def test_cyclical_dependencies(self):
        """verifies that cyclical dependencies are possible"""

        mapping = {'Foo': ['Bar'], 'Bar': ['Foo']}

        self.assertEqual(get_dependencies('Foo', mapping), set(['Foo', 'Bar']))

    def test_resolvable_dependencies(self):
        """verifies that we can resolve all of the dependencies"""
        for base_name in dependencies:
            if base_name.startswith('skins/'):
                project = 'mediawiki/' + base_name
            else:
                project = 'mediawiki/extensions/' + base_name

            self.assertHasDependencies(self.fetch_dependencies(
                project=project))

    def test_job_name(self):
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwext-testextension-hhvm'))
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwext-qunit-jessie'))
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwext-qunit-composer-jessie'))
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwext-mw-selenium-composer-jessie'))
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwext-mw-selenium-jessie'))
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
