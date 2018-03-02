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


class TestMwDependencies(unittest.TestCase):

    def setUp(self):
        # Let test mangle the 'dependencies' global
        self._deps_copy = dependencies.copy()

    def tearDown(self):
        # Restore the 'dependencies' global from the shallow clone
        global dependencies
        dependencies = self._deps_copy
        self.assertIn('AbuseFilter', dependencies)

    def assertHasDependencies(self, params):
        self.assertIn('EXT_DEPENDENCIES', params)

    def assertMissingDependencies(self, params):
        self.assertNotIn('EXT_DEPENDENCIES', params)
        self.assertNotIn('SKIN_DEPENDENCIES', params)

    def fetch_dependencies(self, job_name=None, project=None):
        if project:
            params = {'ZUUL_PROJECT': project}
        else:
            params = {'ZUUL_PROJECT': 'mediawiki/extensions/Example'}
        job = FakeJob(job_name if job_name
                      else 'mwext-testextension-hhvm-jessie')
        set_parameters(None, job, params)
        return params

    def test_ext_name(self):
        params = self.fetch_dependencies(
            project='mediawiki/extensions/Example')

        self.assertIn('EXT_NAME', params)
        self.assertEqual(params['EXT_NAME'], 'Example')

    def test_skin_name(self):
        params = self.fetch_dependencies(
            project='mediawiki/skins/Vector')

        self.assertIn('SKIN_NAME', params)
        self.assertEqual(params['SKIN_NAME'], 'Vector')

    def test_cyclical_dependencies(self):
        """verifies that cyclical dependencies are possible"""

        mapping = {'Foo': ['Bar'], 'Bar': ['Foo']}

        self.assertEqual(get_dependencies('Foo', mapping), set(['Foo', 'Bar']))

    def test_cyclical_dependencies_with_skins(self):
        mapping = {'Foo': ['skins/Vector'], 'skins/Vector': ['Foo']}
        self.assertEqual(
            get_dependencies('skins/Vector', mapping),
            set(['Foo', 'skins/Vector'])
        )

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
            job_name='mwext-testextension-hhvm-jessie'))
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwext-qunit-jessie'))
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwext-qunit-composer-jessie'))
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwext-mw-selenium-composer-jessie'))
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwext-mw-selenium-jessie'))

        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwskin-testskin-hhvm-jessie'))
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwskin-testskin-hhvm-jessie-non-voting'))

        self.assertMissingDependencies(self.fetch_dependencies(
            job_name='mediawiki-core-phplint'))

    def test_zuul_project_name(self):
        self.assertHasDependencies(self.fetch_dependencies(
            project='mediawiki/extensions/Example'))

        self.assertMissingDependencies(self.fetch_dependencies(
            project='mediawiki/extensions'))
        self.assertMissingDependencies(self.fetch_dependencies(
            project='mediawiki/skins'))
        self.assertMissingDependencies(self.fetch_dependencies(
            project='mediawiki/extensions/Example/vendor'))
        self.assertMissingDependencies(self.fetch_dependencies(
            project='foo/bar/baz'))

    def test_vector_skin_added_to_selenium_job(self):
        deps = self.fetch_dependencies(
            job_name='mediawiki-core-qunit-selenium-jessie')
        self.assertDictContainsSubset(
            {'SKIN_DEPENDENCIES': 'mediawiki/skins/Vector'},
            deps
            )

    def test_vector_skin_added_to_mediawiki_core(self):
        # mediawiki/core does not have dependencies, make sure we can append
        # the skin even when SKIN_DEPENDENCIES has not been set previously.
        deps = self.fetch_dependencies(
            job_name='mediawiki-core-qunit-selenium-jessie',
            project='mediawiki/core')
        self.assertDictContainsSubset(
            {'SKIN_DEPENDENCIES': 'mediawiki/skins/Vector'},
            deps
            )

    def test_vector_skin_added_to_selenium_job_on_top_of_other_deps(self):

        # FoobarExt already depends on the monobook skin, we want to make sure
        # we also inject Vector. Global is restored via setUp/tearDown
        global dependencies
        dependencies = {
            'FoobarExt': ['skins/monobook'],
        }
        deps = self.fetch_dependencies(
            project='mediawiki/extensions/FoobarExt',
            job_name='mediawiki-core-qunit-selenium-jessie')
        self.assertIn('SKIN_DEPENDENCIES', deps)
        self.assertEqual(
            deps['SKIN_DEPENDENCIES'],
            'mediawiki/skins/monobook\\nmediawiki/skins/Vector',
        )

    def test_vector_skin_added_to_mwext_mw_selenium(self):
        deps = self.fetch_dependencies(
            project='mediawiki/extensions/Flow',
            job_name='mwext-mw-selenium')
        self.assertIn('SKIN_DEPENDENCIES', deps)
        self.assertIn(
            'mediawiki/skins/Vector',
            deps['SKIN_DEPENDENCIES'].split('\\n')
            )

    def test_resolve_skin_on_extension(self):
        mapping = {'Foo': ['skins/Vector']}
        self.assertEqual(
            get_dependencies('Foo', mapping),
            set(['skins/Vector'])
            )

    def test_resolve_extension_on_skin(self):
        mapping = {'skins/Vector': ['Foo']}
        self.assertEqual(
            get_dependencies('skins/Vector', mapping),
            set(['Foo'])
            )

    def test_resolve_extension_on_extension(self):
        mapping = {'Foo': ['DepExtension']}
        self.assertEqual(
            get_dependencies('Foo', mapping),
            set(['DepExtension'])
            )

    def test_resolve_skin_on_skin(self):
        mapping = {'skins/Child': ['skin/Common']}
        self.assertEqual(
            get_dependencies('skins/Child', mapping),
            set(['skin/Common'])
            )

    def test_inject_skin_on_an_extension(self):
        deps = self.fetch_dependencies(
            job_name='mwext-testextension-hhvm-jessie',
            project='mediawiki/extensions/CustomPage')
        self.assertDictContainsSubset(
            {
                'EXT_NAME': 'CustomPage',
                'SKIN_DEPENDENCIES': 'mediawiki/skins/CustomPage',
            },
            deps)

    def test_inject_extension_on_a_skin(self):
        deps = self.fetch_dependencies(
            job_name='mwskin-testskin-php70-jessie',
            project='mediawiki/skins/BlueSpiceSkin')
        self.assertDictContainsSubset(
            {
                'SKIN_NAME': 'BlueSpiceSkin',
                'EXT_DEPENDENCIES': 'mediawiki/extensions/BlueSpiceFoundation',
            },
            deps)
