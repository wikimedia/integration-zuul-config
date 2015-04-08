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

    def assertProjectHasComposerValidate(self, name, definition, pipeline):
        # php-composer-validate
        # php-composer-validate-package
        # php-composer-test-(zend|hhvm)
        self.assertTrue(
            any([job for job in definition
                 if job.startswith('php-composer')]),
            'Project %s pipeline %s must have either '
            'php-composer-validate or a php-composer-test-* job'
            % (name, pipeline))

    def assertProjectHasPhplint(self, name, definition, pipeline):
        self.assertTrue(
            any([job for job in definition
                 if job.endswith('phplint') or
                 job.startswith('php-composer-test')]),
            'Project %s pipeline %s must have either '
            'phplint or a php-composer-test-* job'
            % (name, pipeline))

    def test_repos_have_required_jobs(self):
        repos = {
            'mediawiki/core$': [
                self.assertProjectHasComposerValidate,
                self.assertProjectHasPhplint
            ],
            'mediawiki/extensions/\w+$': [
                self.assertProjectHasComposerValidate,
                self.assertProjectHasPhplint
            ],
            'mediawiki/skins/': [
                self.assertProjectHasComposerValidate,
                self.assertProjectHasPhplint
            ],
            'mediawiki/vendor$': [
                self.assertProjectHasComposerValidate,
                self.assertProjectHasPhplint
            ],
        }

        for pipeline in self.getPipelines():
            for regex, assertions in repos.items():
                regex_comp = re.compile(regex)
                for name in self.getPipelineProjectsNames(pipeline.name):
                    if regex_comp.match(name):
                        project_def = self.getProjectDef(name)

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

                        for req_pipeline in requirements:
                            # Should be caught by another test:
                            self.assertIn(req_pipeline, project_def.keys(),
                                          'Project %s lacks %s pipeline' %
                                          (name, req_pipeline))
                            for func in assertions:
                                func(name,
                                     project_def[req_pipeline], req_pipeline)

        return

    @unittest.skip('Disabled per T94583, pending overhauling')
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

    def test_valid_jobs_in_check_pipelines(self):
        check_pipelines = [p.name for p in self.getPipelines()
                           if p.name.startswith('check')]

        # Uniq list of projects having a check* pipeline defined
        actual = {}
        # List of jobs allowed in check* pipelines
        safe_jobs = [
            '(php|perl|json|yaml)lint',
            'jshint',
            '.*-(js|perl|shell|php|)lint',
            '(pp|erb)lint-HEAD',
            '.*-(tabs|typos)',
            '.*-pep8',
            '.*-phpcs-HEAD',
            '.*-puppet-validate',
            '.*-puppetlint-(strict|lenient)',
            '.*-pyflakes',
            '(.*-)?ruby(2\.0|1\.9\.3)lint',
            '.*-whitespaces',
            'noop',
            'php-composer-validate',
            'php-composer-package-validate',
        ]
        safe_jobs_re = re.compile('^(' + '|'.join(safe_jobs) + ')$')

        for check_pipeline in check_pipelines:
            actual[check_pipeline] = {}
            for project in self.getPipelineProjectsNames(check_pipeline):
                jobs = self.getProjectDef(project)[check_pipeline]
                unsafe_jobs = [j for j in jobs
                               if not re.match(safe_jobs_re, j)]
                if unsafe_jobs:
                    actual[check_pipeline][project] = unsafe_jobs

        self.maxDiff = None

        # We expect check pipelines to have no unsafe jobs
        expected = {k: {} for k in check_pipelines}
        self.assertEquals(expected, actual)

    def test_recheck_comment_trusted_user(self):
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1:\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_comment_untrusted_user(self):
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1:\n\nrecheck'
        event.account = {'email': 'untrusted@example.org'}
        self.assertFalse(test_manager.eventMatches(event, change))

    def test_pipelines_trustiness(self):
        check_manager = self.getPipeline('check').manager
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')

        # Untrusted user
        untrusted_event = zuul.model.TriggerEvent()
        untrusted_event.type = 'patchset-created'
        untrusted_event.account = {'email': 'untrusted@example.org'}
        self.assertTrue(check_manager.eventMatches(untrusted_event, change))
        self.assertFalse(test_manager.eventMatches(untrusted_event, change))

        # Trusted user
        trusted_event = zuul.model.TriggerEvent()
        trusted_event.type = 'patchset-created'
        trusted_event.account = {'email': 'jdoe@wikimedia.org'}
        self.assertFalse(check_manager.eventMatches(trusted_event, change))
        self.assertTrue(test_manager.eventMatches(trusted_event, change))

    def test_l10nbot_patchets_are_ignored(self):
        managers = [self.getPipeline(p).manager
                    for p in ['check', 'check-only', 'check-voter', 'test']]
        change = zuul.model.Change('mediawiki/core')

        l10n_event = zuul.model.TriggerEvent()
        l10n_event.type = 'patchset-created'
        l10n_event.account = {'email': 'l10n-bot@translatewiki.net'}

        [self.assertFalse(manager.eventMatches(l10n_event, change),
                          'l10-bot should not enter %s pipeline' %
                          manager.pipeline.name)
         for manager in managers]

    # Currently failing since we're ignoring l10n-bot until we can fix
    # issues with CI being overloaded (T91707)
    @unittest.expectedFailure
    def test_l10nbot_allowed_in_gate_and_submit(self):
        gate = self.getPipeline('gate-and-submit').manager
        change = zuul.model.Change('mediawiki/core')

        l10n_event = zuul.model.TriggerEvent()
        l10n_event.type = 'comment-added'
        l10n_event.account = {'email': 'l10n-bot@translatewiki.net'}
        l10n_event.approvals = [{'type': 'Code-Review',
                                 'description': 'Code Review',
                                 'value': '2',
                                 'by': {'email': 'l10n-bot@translatewiki.net'},
                                 }]

        self.assertTrue(gate.eventMatches(l10n_event, change))
