import os
import unittest

from fakes import FakeJob

gatedextensions = None
set_gated_extensions = None

# Import function
execfile(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../zuul/parameter_functions.py'))


class TestSetGatedExtensions(unittest.TestCase):

    def test_deps_applied_on_gate_jobs(self):
        params = {
            'ZUUL_PIPELINE': 'test',
            'ZUUL_PROJECT': 'mediawiki/core',
        }
        gate_job = FakeJob('mediawiki-extensions-foo')
        set_gated_extensions(None, gate_job, params)
        self.assertIn('EXT_DEPENDENCIES', params)

    def test_experimental_injects_project(self):
        params = {
            'ZUUL_PIPELINE': 'experimental',
            'ZUUL_PROJECT': 'mediawiki/extensions/SomeExt',
        }
        gate_job = FakeJob('mediawiki-extensions-foo')
        set_gated_extensions(None, gate_job, params)
        self.assertIn('\\nmediawiki/extensions/SomeExt',
                      params['EXT_DEPENDENCIES'])
