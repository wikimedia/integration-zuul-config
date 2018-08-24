# Generate Jenkins jobs

import argparse
from glob import glob
import os
import shutil
import tempfile
import unittest

from jenkins_jobs.cli.entry import JenkinsJobs
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

        config_file = os.path.join(
            os.path.dirname(__file__),
            'fixtures/jjb-disable-query-plugins.conf')
        jjb_test = JenkinsJobs(args=[
            '--conf', config_file,
            'test', jjb_dir, '-o', out_dir])
        jjb_test.execute()

    # Merely to show that the config has been generated in setUpClass
    def test_jjb_generate_jobs(self):
        self.assertNotEqual(
            [], os.listdir(self.jjb_out_dir),
            'jjb must have generated jobs')

    def test_jenkins_jobs_have_a_timeout(self):
        lack_timeout = []
        for job_file in glob(self.jjb_out_dir + '/*'):
            with open(job_file) as f:
                if 'BuildTimeoutWrapper' not in f.read():
                    lack_timeout.append(os.path.basename(f.name))

        self.maxDiff = None
        self.longMessage = True
        self.assertEquals(
            [], lack_timeout,
            'All Jenkins jobs must have a timeout')

    def test_jjb_zuul_jobs(self):
        'Zuul jobs are defined by JJB'

        jjb_jobs_file = tempfile.NamedTemporaryFile()
        jjb_jobs_file.write(
            "\n".join(os.listdir(self.jjb_out_dir)))
        jjb_jobs_file.flush()

        this_dir = os.path.dirname(os.path.abspath(__file__))

        zuul_server = zuul.cmd.server.Server()
        zuul_server.args = argparse.Namespace(
            config=os.path.join(this_dir, 'fixtures/zuul-dummy.conf'),
            validate=jjb_jobs_file.name,
        )
        zuul_server.read_config()
        zuul_server.config.set(
            'zuul', 'layout_config',
            os.path.join(this_dir, '../zuul/layout.yaml'))

        self.assertFalse(zuul_server.test_config(jjb_jobs_file.name))
