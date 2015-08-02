import os
import unittest

from fakes import FakeItemChange

set_doc_variables = None  # defined for flake8
# Import function
execfile(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../zuul/doc_functions.py'))


class TestDocFunctions(unittest.TestCase):

    def assertDocSubpath(self, expected, item):
        params = {}
        set_doc_variables(item, None, params)
        self.assertIn(
            'DOC_SUBPATH', params,
            "Missing parameter: 'DOC_SUBPATH': %s" % expected)
        self.assertEqual(expected, params.get('DOC_SUBPATH'))

    def assertNoDocSubpath(self, item):
        params = {}
        set_doc_variables(item, None, params)
        self.assertNotIn('DOC_SUBPATH', params,
                         'DOC_SUBPATH should not be set')

    def test_change_with_no_ref_nor_refspec(self):
        self.assertNoDocSubpath(FakeItemChange('master'))

    def test_change_with_ref(self):
        self.assertDocSubpath(
            'master',
            FakeItemChange('master', refspec='refs/changes/34/1234/8'))

    def test_ref_updated_branch(self):
        self.assertDocSubpath(
            'master',
            # ref-updated events give the branch ref as a short version!
            FakeItemChange('', ref='master'))

    def test_ref_updated_tag(self):
        self.assertDocSubpath(
            '42.0',
            FakeItemChange('', ref='refs/tags/42.0'))

    def test_set_doc_project(self):
        projects = {
            'oojs/ui': 'oojs-ui',
            'wikimedia/slimapp': 'wikimedia-slimapp',
            'cdb': 'cdb'
        }
        for project, expected in projects.items():
            params = {'ZUUL_PROJECT': project}
            set_doc_variables(FakeItemChange('', ref='master'), None, params)
            self.assertEqual(params['DOC_PROJECT'], expected)
