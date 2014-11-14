import os
import unittest

set_doc_subpath = None  # defined for flake8
# Import function
execfile(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../zuul/doc_functions.py'))


class FakeChange(object):

    def __init__(self, branch, ref=None, refspec=None):
        self.branch = branch
        if ref:
            self.ref = ref
        if refspec:
            self.refspec = refspec


class FakeItemChange(object):

    def __init__(self, *args, **kwargs):
        self.change = FakeChange(*args, **kwargs)


class TestDocFunctions(unittest.TestCase):

    def assertDocSubpath(self, expected, item):
        params = {}
        set_doc_subpath(item, None, params)
        self.assertIn(
            'DOC_SUBPATH', params,
            "Missing parameter: 'DOC_SUBPATH': %s" % expected)
        self.assertEqual(expected, params.get('DOC_SUBPATH'))

    def assertNoDocSubpath(self, item):
        params = {}
        set_doc_subpath(item, None, params)
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
