# Generate Jenkins jobs

import argparse
import os
import shutil
import tempfile
import unittest

from jenkins_jobs.cmd import main as jjb
import zuul.cmd.server


class IntegrationTests(unittest.TestCase):

    jjb_out_dir = None

    @classmethod
    def setUpClass(cls):
        cls.jjb_out_dir = tempfile.mkdtemp()
        cls.generate_jjb_jobs(cls.jjb_out_dir)

    @classmethod
    def tearDownClass(cls):
        if cls.jjb_out_dir:
            shutil.rmtree(cls.jjb_out_dir)

    @staticmethod
    def generate_jjb_jobs(out_dir):
        jjb_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../jjb')
        jjb(argv=['test', jjb_dir, '-o', out_dir])

    # Merely to show that the config has been generated in setUpClass
    def test_has_generated_jobs(self):
        self.assertNotEqual(
            [], os.listdir(self.jjb_out_dir),
            'jjb must have generated jobs')

    def test_jjb_zuul_jobs(self):
        jjb_jobs_file = tempfile.NamedTemporaryFile()
        jjb_jobs_file.write(
            "\n".join(os.listdir(self.jjb_out_dir)))

        this_dir = os.path.dirname(os.path.abspath(__file__))

        zuul_server = zuul.cmd.server.Server()
        zuul_server.args = argparse.Namespace(
            config=os.path.join(this_dir, 'fixtures/zuul-dummy.conf'),
            layout=os.path.join(this_dir, '../zuul/layout.yaml'),
            validate=jjb_jobs_file.name,
        )
        zuul_server.read_config()
        zuul_server.config.set(
            'zuul', 'layout_config', zuul_server.args.layout)

        self.assertFalse(zuul_server.test_config(jjb_jobs_file.name))
