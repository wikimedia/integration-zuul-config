# Verify Wikimedia Zuul layout functionalities
#
# Copyright (c) 2014 - Antoine "hashar" Musso
# Copyright (c) 2014 - Wikimedia Foundation Inc.

import ConfigParser
import re
import os
import unittest

import zuul.scheduler
from zuul.scheduler import ReconfigureEvent
import zuul.model


class FakeTrigger(object):

    """
    Simulate a Zuul trigger.

    When the scheduler is reconfigured, it calls maintainCache() on each
    trigger.
    """

    def maintainCache(self, relevant):
        return

    def postConfig(self):
        return


class TestZuulLayout(unittest.TestCase):

    zuul_config = None
    sched = None

    def __init__(self, *args, **kwargs):
        super(TestZuulLayout, self).__init__(*args, **kwargs)

        # Craft our own zuul.conf
        wmf_zuul_layout = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../zuul/layout.yaml')
        cfg = ConfigParser.ConfigParser()
        cfg.add_section('zuul')
        cfg.set('zuul', 'layout_config', wmf_zuul_layout)
        self.zuul_config = cfg

        self.sched = zuul.scheduler.Scheduler()
        # Reporters and Triggers are registered by zuul-server, not the
        # Scheduler class:
        self.sched.registerTrigger(FakeTrigger(), 'gerrit')
        self.sched.registerTrigger(FakeTrigger(), 'timer')
        self.sched.registerTrigger(FakeTrigger(), 'zuul')
        self.sched._doReconfigureEvent(ReconfigureEvent(self.zuul_config))

    # Helpers

    def getPipeline(self, name):
        """Return the Pipeline object for name"""
        pipeline = self.sched.layout.pipelines.get(name)
        if pipeline is None:
            raise Exception("No such pipeline: %s" % name)
        return pipeline

    def getPipelines(self):
        """Returns all pipeline objects"""
        return self.sched.layout.pipelines.values()

    def getPipelineProjects(self, pipeline_name):
        """Returns Projects object for given pipeline"""
        return self.getPipeline(pipeline_name).getProjects()

    def getPipelineProjectsNames(self, pipeline_name):
        """Returns name of projects for a given pipeline"""
        return [p.name for p in self.getPipeline(pipeline_name).getProjects()]

    def getProjectDef(self, project):
        """Returns pipelines and their jobs for a given project"""
        ret = {}
        for pipeline in self.sched.layout.pipelines.values():

            if project not in [pj.name for pj in pipeline.getProjects()]:
                continue

            tree = [t for (p, t) in pipeline.job_trees.iteritems()
                    if p.name == project]
            ret[pipeline.name] = [job.name for job in tree[0].getJobs()]
        return ret

    # Tests

    def test_mw_repos_have_composer_validate_job(self):
        mw_repos = (
            'mediawiki/core$',
            'mediawiki/extensions/\w+$',
            'mediawiki/skins/',
            'mediawiki/vendor$',
        )
        re_mw = '(' + '|'.join(mw_repos) + ')'

        # Mediawiki projects defined in any pipeline
        mw_projects = set()
        for pipeline in self.getPipelines():
            mw_projects |= set(
                [p for p in self.getPipelineProjectsNames(pipeline.name)
                 if re.match(re_mw, p)])
        mw_projects = sorted(mw_projects)

        for mw_project in mw_projects:
            project_def = self.getProjectDef(mw_project)

            requirements = set()
            requirements.add('gate-and-submit')

            if 'check-only' in project_def.keys():
                requirements.add('check-only')
            elif 'check-voter' in project_def.keys():
                # Skins uses a different check pipeline
                requirements.add('check-voter')
            else:
                requirements.add('check')
                requirements.add('test')

            for pipeline in requirements:
                # Should be caught by another test:
                self.assertIn(pipeline, project_def.keys(),
                              'Project %s lacks %s pipeline' %
                              (mw_project, pipeline))
                self.assertTrue(
                    ('php-composer-validate' in project_def[pipeline]) or any(
                        [job for job in project_def[pipeline]
                            if re.search('-composer$', job)]),
                    'Project %s pipeline %s must have either '
                    'php-composer-validate or a *-composer job'
                    % (mw_project, pipeline))

        return

    def test_release_mediawiki_non_wmf_version_tags(self):

        # Get the mediawiki-core-release job
        publish_trees = self.sched.layout.pipelines['publish'].job_trees
        tree = [t for (p, t) in publish_trees.iteritems()
                if p.name == 'mediawiki/core']
        rel_job = [j for j in tree[0].getJobs()
                   if j.name == 'mediawiki-core-release']
        rel_job = rel_job[0]

        # Zuul representaiton of a Gerrit ref-updated event
        ref = zuul.model.Ref('mediawiki/core')

        # We dont create mw releases on wmf tags
        ref.ref = 'refs/tags/wmf/1.24wmf13'
        self.assertFalse(rel_job.changeMatches(ref))

        # We do create release for public versions
        ref.ref = 'refs/tags/1.24.0'
        self.assertTrue(rel_job.changeMatches(ref))
        ref.ref = 'refs/tags/1.24.0-rc.0'
        self.assertTrue(rel_job.changeMatches(ref))
        ref.ref = 'refs/tags/2.0'
        self.assertTrue(rel_job.changeMatches(ref))
