import os
import unittest

from fakes import FakeItemChange

set_distributions = None  # defined for flake8
# Import function
execfile(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../zuul/debian_glue_functions.py'))


class TestDebianGlueFunctions(unittest.TestCase):

    def assertDistributions(self, expected, item, job_params={}):
        set_distributions(item, None, job_params)
        self.assertEquals(expected,
                          job_params.get('DEBIAN_GLUE_DISTRIBUTIONS'))

    def test_default_to_sid(self):
        self.assertDistributions('sid', FakeItemChange('master'))
        self.assertDistributions('sid', FakeItemChange('debian'))

    def test_recognize_debian_branches(self):
        self.assertDistributions('precise', FakeItemChange('debian/precise'))
        self.assertDistributions('jessie', FakeItemChange('debian/jessie'))
        self.assertDistributions('sid', FakeItemChange('debian/sid'))
        self.assertDistributions('jessie-wikimedia',
                                 FakeItemChange('debian/jessie-wikimedia'))
