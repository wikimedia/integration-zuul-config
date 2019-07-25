import os

import pytest
from fakes import FakeJob

dependencies = {}  # defined for flake8
get_dependencies = None  # defined for flake8
set_parameters = None  # defined for flake8
# Import function
execfile(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../zuul/parameter_functions.py'))


class TestMwDependencies:

    def assertHasDependencies(self, params):
        assert 'EXT_DEPENDENCIES' in params

    def assertMissingDependencies(self, params):
        assert 'EXT_DEPENDENCIES' not in params
        assert 'SKIN_DEPENDENCIES' not in params

    def fetch_dependencies(self, job_name=None, project=None, branch='master'):
        if project:
            params = {'ZUUL_PROJECT': project}
        else:
            params = {'ZUUL_PROJECT': 'mediawiki/extensions/Example'}
        params['ZUUL_BRANCH'] = branch

        job = FakeJob(job_name if job_name
                      else 'mediawiki-quibble-composer-mysql-php70-docker')
        set_parameters(None, job, params)
        return params

    def test_ext_name(self):
        params = self.fetch_dependencies(
            project='mediawiki/extensions/Example')

        assert 'EXT_NAME' in params
        assert params['EXT_NAME'] == 'Example'

    def test_skin_name(self):
        params = self.fetch_dependencies(
            project='mediawiki/skins/Vector')

        assert 'SKIN_NAME' in params
        assert params['SKIN_NAME'] == 'Vector'

    def test_cyclical_dependencies(self):
        """verifies that cyclical dependencies are possible"""

        mapping = {'Foo': ['Bar'], 'Bar': ['Foo']}

        assert get_dependencies('Foo', mapping) == set(['Foo', 'Bar'])

    def test_cyclical_dependencies_with_skins(self):
        mapping = {'Foo': ['skins/Vector'], 'skins/Vector': ['Foo']}
        assert get_dependencies('skins/Vector', mapping) \
            == set(['Foo', 'skins/Vector'])

    @pytest.mark.parametrize('base_name', dependencies)
    def test_resolvable_dependencies(self, base_name):
        """verifies that we can resolve all of the dependencies"""
        if base_name.startswith('skins/'):
            project = 'mediawiki/' + base_name
        else:
            project = 'mediawiki/extensions/' + base_name

        self.assertHasDependencies(self.fetch_dependencies(
            project=project))

    def test_job_name(self):
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mediawiki-quibble-composer-mysql-php70-docker'))
        self.assertHasDependencies(self.fetch_dependencies(
            job_name='mwselenium-quibble-docker'))

        self.assertHasDependencies(self.fetch_dependencies(
            job_name='quibble-composer-mysql-php70-docker'))

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

    def test_resolve_skin_on_extension(self):
        mapping = {'Foo': ['skins/Vector']}
        assert get_dependencies('Foo', mapping) == set(['skins/Vector'])

    def test_resolve_extension_on_skin(self):
        mapping = {'skins/Vector': ['Foo']}
        assert get_dependencies('skins/Vector', mapping) == set(['Foo'])

    def test_resolve_extension_on_extension(self):
        mapping = {'Foo': ['DepExtension']}
        assert get_dependencies('Foo', mapping) == set(['DepExtension'])

    def test_resolve_skin_on_skin(self):
        mapping = {'skins/Child': ['skin/Common']}
        assert get_dependencies('skins/Child', mapping) == set(['skin/Common'])

    def test_no_recursion(self):
        mapping = {
            'A': ['B'],
            'B': ['C'],
        }
        assert get_dependencies('A', mapping, recurse=False) == set(['B'])

    def test_inject_skin_on_an_extension(self):
        deps = self.fetch_dependencies(
            job_name='mediawiki-quibble-composer-mysql-php70-docker',
            project='mediawiki/extensions/CustomPage')
        assert deps['EXT_NAME'] == 'CustomPage'
        assert deps['SKIN_DEPENDENCIES'] == 'mediawiki/skins/CustomPage'

    def test_inject_extension_on_a_skin(self):
        deps = self.fetch_dependencies(
            job_name='quibble-composer-mysql-php70-docker',
            project='mediawiki/skins/BlueSpiceSkin')
        assert deps['SKIN_NAME'] == 'BlueSpiceSkin'
        assert deps['EXT_DEPENDENCIES'] == '%s\\n%s' % (
            'mediawiki/extensions/BlueSpiceFoundation',
            'mediawiki/extensions/ExtJSBase')

    def test_inject_dependencies_on_quibble_jobs(self):
        deps = self.fetch_dependencies(
            job_name='quibble-composer-mysql-php70-docker',
            project='mediawiki/extensions/PropertySuggester')
        assert 'EXT_DEPENDENCIES' in deps
        assert '\\nmediawiki/extensions/Wikibase\\n' \
               in deps['EXT_DEPENDENCIES']

    def test_bluespice_branch_exception(self):
        deps = self.fetch_dependencies(
            job_name='quibble-composer-mysql-php70-docker',
            project='mediawiki/extensions/BlueSpiceFoundation')

        assert 'EXT_DEPENDENCIES' in deps
        assert 'mediawiki/extensions/ExtJSBase' == deps['EXT_DEPENDENCIES']

        # Ditto but with REL1_27
        deps = self.fetch_dependencies(
            job_name='quibble-composer-mysql-php70-docker',
            project='mediawiki/extensions/BlueSpiceFoundation',
            branch='REL1_27')
        assert 'EXT_DEPENDENCIES' in deps
        assert 'mediawiki/extensions/ExtJSBase' not \
               in deps['EXT_DEPENDENCIES'], \
            'BlueSpice@REL1_27 must not depend on ExtJSBase T196454'
