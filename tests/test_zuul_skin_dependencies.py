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


class TestSkinDependencies(unittest.TestCase):
    def assertHasDependencies(self, params):
        self.assertIn('EXT_DEPENDENCIES', params)

    def assertMissingDependencies(self, params):
        self.assertNotIn('EXT_DEPENDENCIES', params)

    def fetch_dependencies(self, job_name=None, project=None):
        if project:
            params = {'ZUUL_PROJECT': project}
        else:
            params = {'ZUUL_PROJECT': 'mediawiki/skins/Example'}
        job = FakeJob(job_name if job_name else 'mw-testskin')
        set_parameters(None, job, params)
        return params

    def test_skin_name(self):
        params = self.fetch_dependencies(
            project='mediawiki/skins/Example')

        self.assertIn('EXT_NAME', params)
        self.assertEqual(params['EXT_NAME'], 'Example')

    def test_cyclical_dependencies(self):
        """verifies that cyclical dependencies are possible"""

        mapping = {'Foo': ['Bar'], 'Bar': ['Foo']}

        self.assertEqual(get_dependencies('Foo', mapping), set(['Foo', 'Bar']))

    def test_resolvable_dependencies(self):
        """verifies that we can resolve all of the dependencies"""
        for ext_name in dependencies:
            self.assertHasDependencies(self.fetch_dependencies(
                project='mediawiki/' + ext_name))

    def test_job_name(self):
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mw-testskin'))
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mw-testskin-non-voting'))
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
