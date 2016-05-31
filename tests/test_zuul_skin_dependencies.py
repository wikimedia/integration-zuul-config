import os
import unittest

from fakes import FakeJob

skin_dependencies = {}  # defined for flake8
get_skin_dependencies = None  # defined for flake8
set_parameters = None  # defined for flake8
# Import function
execfile(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../zuul/parameter_functions.py'))


class TestSkinDependencies(unittest.TestCase):
    def assertHasDependencies(self, params):
        self.assertIn('SKIN_DEPENDENCIES', params)

    def assertMissingDependencies(self, params):
        self.assertNotIn('SKIN_DEPENDENCIES', params)

    def fetch_dependencies(self, job_name=None, project=None):
        if project:
            params = {'ZUUL_PROJECT': project}
        else:
            params = {'ZUUL_PROJECT': 'mediawiki/skins/Example'}
        job = FakeJob(job_name if job_name else 'mwskin-testskin-hhvm')
        set_parameters(None, job, params)
        return params

    def test_skin_name(self):
        params = self.fetch_dependencies(
            project='mediawiki/skins/Example')

        self.assertIn('SKIN_NAME', params)
        self.assertEqual(params['SKIN_NAME'], 'Example')

    def test_cyclical_dependencies(self):
        """verifies that cyclical dependencies are possible"""

        mapping = {'Foo': ['Bar'], 'Bar': ['Foo']}

        self.assertEqual(
            get_skin_dependencies('Foo', mapping), set(['Foo', 'Bar']))

    def test_resolvable_dependencies(self):
        """verifies that we can resolve all of the dependencies"""
        for skin_name in skin_dependencies:
            self.assertHasDependencies(self.fetch_dependencies(
                project='mediawiki/skins/' + skin_name))

    def test_job_name(self):
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwskin-testskin-hhvm'))
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwskin-qunit'))
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwskin-mw-selenium'))
        self.assertMissingDependencies(self.fetch_dependencies(
            job_name='mediawiki-core-phplint'))

    def test_zuul_project_name(self):
        self.assertHasDependencies(self.fetch_dependencies(
            project='mediawiki/skins/Example'))
        self.assertMissingDependencies(self.fetch_dependencies(
            project='mediawiki/skins'))
        self.assertMissingDependencies(self.fetch_dependencies(
            project='mediawiki/skins/Example/vendor'))
        self.assertMissingDependencies(self.fetch_dependencies(
            project='foo/bar/baz'))
