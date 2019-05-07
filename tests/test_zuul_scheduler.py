# Verify Wikimedia Zuul scheduler functionalities
#
# Copyright (c) 2014 - Antoine "hashar" Musso
# Copyright (c) 2014 - Wikimedia Foundation Inc.

import ConfigParser
import re
import shutil
import tempfile
import os
import unittest

import zuul.scheduler
from zuul.scheduler import ReconfigureEvent
from zuul.reporter.gerrit import GerritReporter
import zuul.model

from zuul.connection import BaseConnection
from zuul.connection.gerrit import GerritConnection


class FakeConnection(BaseConnection):
    """
    Simulate a Zuul connection
    """

    def __init__(self, connection_name, connection_config):
        super(FakeConnection, self).__init__(connection_name,
                                             connection_config)
        self.driver_name = connection_name


class TestZuulScheduler(unittest.TestCase):

    sched = None

    @classmethod
    def setUpClass(cls):
        # Craft our own zuul.conf
        wmf_zuul_layout = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../zuul/layout.yaml')
        cfg = ConfigParser.ConfigParser()
        cfg.add_section('zuul')
        cfg.set('zuul', 'layout_config', wmf_zuul_layout)

        cls.state_dir = tempfile.mkdtemp()
        cfg.set('zuul', 'state_dir', cls.state_dir)

        # Reporters and Triggers are registered by zuul-server, not the
        # Scheduler class:
        cls.sched = zuul.scheduler.Scheduler(cfg)
        cls.sched.registerConnections({
            'gerrit': FakeConnection('gerrit', {})
        })
        cls.sched._doReconfigureEvent(ReconfigureEvent(cfg))

    @classmethod
    def tearDownClass(cls):
        cls.sched.exit()
        if cls.state_dir:
            shutil.rmtree(cls.state_dir)

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

    def getProjectsDefs(self):
        """Map projects, pipelines and their jobs (as strings, not objects)"""
        ret = {}
        for pipeline in self.sched.layout.pipelines.values():
            for (project, tree) in pipeline.job_trees.iteritems():
                ret.setdefault(project.name, {})[pipeline.name] = \
                    [job.name for job in tree.getJobs()]
        return ret

    def getJob(self, project, pipeline, job):
        """
        project: Gerrit project name
        pipeline: Zuul pipeline
        job: Job name to fetch for that project/pipeline
        """
        job_tree = [
            t for (p, t) in
            self.getPipeline(pipeline).job_trees.iteritems()
            if p.name == project][0]

        try:
            job = [
                j for j in job_tree.getJobs()
                if j.name == job][0]
        except IndexError:
            raise Exception('No such job %s for %s in pipeline %s' % (
                job, project, pipeline))

        return job

    def test_only_voting_jobs_in_gate(self):
        gate = self.getPipeline('gate-and-submit')
        non_voting = {}
        for gated_project in gate.getProjects():
            for job in gate.getJobTree(gated_project).getJobs():
                if not job.voting:
                    non_voting.setdefault(
                        gated_project.name, []
                    ).append(job.name)
        self.longMessage = True
        self.maxDiff = None
        self.assertDictEqual(
            {}, non_voting,
            'non voting jobs are not allowed in gate-and-submit')

    def getProjectsPipelines(self):
        """Map of projects -> pipelines names"""
        projects_pipelines = {}
        for pipeline in self.getPipelines():
            for project in self.getPipelineProjectsNames(pipeline.name):
                projects_pipelines.setdefault(project, []) \
                                  .append(pipeline.name)
        return projects_pipelines

    # Tests

    def assertProjectHasComposerValidate(self, name, definition, pipeline):
        # composer-validate-package
        # composer-test-(zend|hhvm)
        # mwgate-composer-*
        if pipeline in ['experimental', 'gate-and-submit-l10n']:
            return
        self.assertTrue(
            any([job for job in definition
                 if (
                     job.startswith(('composer', 'mwgate-composer'))
                     or job.startswith('quibble-')
                     or job.startswith('wmf-quibble-')
                 )]),
            'Project %s pipeline %s must have either '
            'composer-validate or a composer-* job, '
            'has: %s'
            % (name, pipeline, definition))

    def assertProjectHasPhplint(self, name, definition, pipeline):
        if pipeline in ['experimental', 'gate-and-submit-l10n']:
            return
        self.assertTrue(
            any([job for job in definition
                 if job.startswith('quibble-')
                 or job.startswith('wmf-quibble')
                 or job.startswith(('composer-', 'mwgate-composer'))]),
            'Project %s pipeline %s must have either a composer-* job'
            % (name, pipeline))

    def assertProjectHasPhp55Test(self, name, definition, pipeline):
        if pipeline != 'php5' or pipeline != 'gate-and-submit':
            return
        for job in definition:
            if 'testextension-hhvm' in job:
                self.assertTrue(True)
                return
        self.assertTrue(False, 'Project %s pipeline %s must have a '
                        'php55 test job' % (name, pipeline))

    def assertProjectHasSkinTests(self, name, definition, pipeline):
        if pipeline != 'test':
            return
        self.assertTrue(
            any([job for job in definition
                 if job.startswith('quibble-')]),
            'Project %s pipeline %s must have job '
            'starting with quibble-'
            % (name, pipeline)
            )

    def assertProjectHasExperimentalPhan(self, name, definition, pipeline):
        if pipeline != 'experimental':
            return
        self.assertTrue(
            any([job for job in definition
                 if job.endswith('phan-docker')]),
            'Project %s pipeline %s must have job '
            'ending with phan-docker'
            % (name, pipeline)
            )

    def assertProjectHasNoExtensionTests(self, name, definition, pipeline):
        self.longMessage = True
        self.assertEqual(
            [],
            [job for job in definition if 'testextension' in job],
            'Project %s pipeline %s cannot have "testextension" jobs'
            % (name, pipeline)
        )

    def assertProjectHasVotingPHP71(self, name, definition, pipeline):
        if pipeline != 'gate-and-submit':
            return
        self.assertTrue(
            any([job for job in definition
                 if 'quibble' in job and 'php71' in job]),
            'Project %s pipeline %s must have job '
            'for PHP 7.1 quibble'
            % (name, pipeline)
            )

    def assertQuibbleHasNpmTest(self, name, definition, pipeline):
        if pipeline != 'experimental':
            return
        has_quibble = any([job for job in definition if 'quibble' in job])
        has_npm_test = any([job for job in definition if 'npm-node-6' in job])
        self.assertEqual(has_npm_test, has_quibble,
                         'Project %s pipeline %s must have both quibble and '
                         'npm job' % (name, pipeline))

    def assertProjectHasI18nChecker(self, name, definition, pipeline):
        if pipeline != 'gate-and-submit-l10n':
            return
        self.assertTrue(
            any([job for job in definition
                 if 'mediawiki-i18n-check-docker' == job]),
            'Project %s pipeline %s must have job mediawiki-i18n-check-docker'
            % (name, pipeline)
            )

    def test_repos_have_required_jobs(self):
        repos = {
            r'mediawiki/core$': [
                self.assertProjectHasComposerValidate,
                self.assertProjectHasPhplint,
                self.assertProjectHasVotingPHP71,
                self.assertProjectHasI18nChecker,
            ],
            r'mediawiki/extensions/\w+$': [
                self.assertProjectHasComposerValidate,
                self.assertProjectHasPhplint,
                self.assertProjectHasPhp55Test,
                self.assertProjectHasExperimentalPhan,
                self.assertProjectHasI18nChecker,
            ],
            r'mediawiki/skins/': [
                self.assertProjectHasComposerValidate,
                self.assertProjectHasPhplint,
                self.assertProjectHasSkinTests,
                self.assertProjectHasNoExtensionTests,
                self.assertProjectHasExperimentalPhan,
                self.assertProjectHasI18nChecker,
            ],
            r'mediawiki/vendor$': [
                self.assertProjectHasComposerValidate,
                self.assertProjectHasPhplint,
                self.assertProjectHasI18nChecker,
            ],
        }

        # Pre compile above regular expressions
        repos_compiled = {}
        for (regex, assertions) in repos.iteritems():
            repos_compiled[re.compile(regex)] = assertions
        del repos

        # Dict of projects -> assertions
        mediawiki_projects = {}
        for project_name in self.getProjectsPipelines().keys():
            project_assertions = None
            for regex_compiled, assertions in repos_compiled.items():
                if regex_compiled.match(project_name):
                    project_assertions = assertions
                    break
            # Project did not match
            if project_assertions is None:
                continue
            mediawiki_projects[project_name] = assertions

        all_defs = self.getProjectsDefs()
        for (project_name, assertions) in mediawiki_projects.iteritems():

            project_def = all_defs[project_name]

            # If the project is archived, skip it
            if 'gate-and-submit' in project_def:
                gate_jobs = project_def['gate-and-submit']
                if 'fail-archived-repositories' in gate_jobs:
                    continue

            # Pipelines that must be set
            requirements = {'gate-and-submit', 'experimental'}
            for default_requirement in [
                    'test', 'gate-and-submit-l10n']:
                requirements.add(default_requirement)
                self.assertIn(default_requirement, project_def.keys(),
                              'Project %s must have a %s pipeline'
                              % (project_name, default_requirement))

            # Validate the pipeline has the proper jobs
            for req_pipeline in requirements:
                for func in assertions:
                    func(project_name,
                         project_def.get(req_pipeline, []), req_pipeline)

        return

    def test_projects_have_pipeline_gate_and_submit(self):
        lacks_gate = []
        for (project, pipelines) in self.getProjectsPipelines().iteritems():
            if(
                'gate-and-submit' in pipelines
                # Zuul account cant merge for ops:
                or project.startswith('operations/')
                # Weird edge cases:
                or project in [
                    'integration/zuul',
                    'mediawiki/debian',
                    ]
                # Some repos just have experimental:
                or pipelines == ['experimental']
            ):
                continue
            lacks_gate.append(project)

        self.maxDiff = None
        self.assertEqual([], lacks_gate)

    def assertPipelinesDoNotOverlap(self, pipeline_name_1, pipeline_name_2,
                                    msg=None):
        first = set(self.getPipelineProjectsNames(pipeline_name_1))
        second = set(self.getPipelineProjectsNames(pipeline_name_2))

        self.longMessage = True
        self.maxDiff = None
        self.assertEqual(set(), first & second, msg)

    def test_post_on_ref_update(self):
        manager = self.getPipeline('post').manager

        change = zuul.model.Change('mediawiki/core')

        event = zuul.model.TriggerEvent()
        event.type = 'ref-updated'
        event.ref = 'refs/heads/wmf/1.29.0-wmf.20'

        self.assertTrue(manager.eventMatches(event, change))

    def test_no_post_on_ref_tag_update(self):
        manager = self.getPipeline('post').manager

        change = zuul.model.Change('mediawiki/core')

        event = zuul.model.TriggerEvent()
        event.type = 'ref-updated'
        event.ref = 'refs/tags/wmf/1.29.0-wmf.20'

        self.assertFalse(manager.eventMatches(event, change))

    def test_gate_and_submit_swat(self):
        gs_swat_manager = self.getPipeline('gate-and-submit-swat').manager
        gs_manager = self.getPipeline('gate-and-submit').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'wmf/1.29.0-wmf.20'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Code-Review+2'
        event.branch = change.branch
        event.approvals = [{
            'description': 'Code-Review', 'type': 'CRVW', 'value': '2'}]

        self.assertTrue(gs_swat_manager.eventMatches(event, change))
        self.assertFalse(gs_manager.eventMatches(event, change))

    def test_recheck_comment_trusted_user(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1:\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_comment_untrusted_user(self):
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1:\n\nrecheck'
        event.account = {'email': 'untrusted@example.org'}
        event.branch = change.branch

        self.assertFalse(test_manager.eventMatches(event, change))

    def test_recheck_comment_untrusted_user_with_code_review(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: -Code-Review\n\nrecheck'
        event.account = {'email': 'untrusted@example.org'}
        event.branch = change.branch

        self.assertFalse(test_manager.eventMatches(event, change))

    def test_recheck_with_code_review_vote_removed(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: -Code-Review\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_with_verified_vote_removed(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: -Verified\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertFalse(test_manager.eventMatches(event, change))

    def test_recheck_with_code_review_vote_plus_one(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Code-Review+1\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_with_code_review_vote_plus_two(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Code-Review+2\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_with_code_review_vote_minus_one(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Code-Review-1\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_with_code_review_vote_minus_two(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Code-Review-2\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_with_verified_vote_minus_two(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Verified-2\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertFalse(test_manager.eventMatches(event, change))

    def test_recheck_with_verified_vote_minus_one(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Verified-1\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertFalse(test_manager.eventMatches(event, change))

    def test_recheck_with_verified_vote_plus_one(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Verified+1\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertFalse(test_manager.eventMatches(event, change))

    def test_recheck_with_verified_vote_plus_2(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Verified+2\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertFalse(test_manager.eventMatches(event, change))

    def test_recheck_with_inline_comment(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1:\n\n(1 comment)\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_with_inline_comment_changed_review(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Code-Review+1\n\n(1 comment)\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_with_inline_comment_removed_review(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: -Code-Review\n\n(2 comments)\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_comment_trusted_user_extra_comment_1(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        extra_comment = 'recheck because CI failed due to Txxxxxx'
        event.comment = 'Patch Set 1:\n\n' + extra_comment
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_comment_trusted_user_extra_comment_2(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        extra_comment = 'recheck \u2013 Jenkins failure looks unrelated'
        event.comment = 'Patch Set 1:\n\n' + extra_comment
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_comment_trusted_user_extra_comment_3(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        extra_comment = 'recheck, is it still failing?'
        event.comment = 'Patch Set 1:\n\n' + extra_comment
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_comment_trusted_user_recheck_buried_in_comment_1(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        extra_comment = "let's wait a bit before recheck, Zuul looks busy"
        event.comment = 'Patch Set 1:\n\n' + extra_comment
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertFalse(test_manager.eventMatches(event, change))

    def test_recheck_comment_trusted_user_recheck_buried_in_comment_2(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        extra_comment = 'a recheck will not help here, you need to fix this'
        event.comment = 'Patch Set 1:\n\n' + extra_comment
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.branch = change.branch

        self.assertFalse(test_manager.eventMatches(event, change))

    def test_recheck_on_approved_change_triggers_gate(self):
        user_comment = 'recheck'
        gate_manager = self.getPipeline('gate-and-submit').manager

        change = zuul.model.Change(self.sched.getProject('mediawiki/core'))
        change.branch = 'master'
        # Change already has received a code-review +2
        change.approvals = [{'type': 'Code-Review',
                             'description': 'Code Review',
                             'value': '2',
                             'by': {'email': 'someone@wikimedia.org'},
                             }]

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1:\n\n%s' % user_comment
        event.branch = change.branch
        # Gerrit comment-added event carries the patch approvals
        event.approvals = change.approvals

        self.assertTrue(
            gate_manager.eventMatches(event, change),
            "gate-and-submit must accepts '%s' on a change having CR+2" % (
                user_comment)
        )

    def test_test_pipelines_reject_approved_changes(self):
        indep_pipelines = [
            p for p in self.getPipelines()
            if p.manager.__class__.__name__ == 'IndependentPipelineManager']

        self.assertGreater(len(indep_pipelines), 0)

        errors = []

        # Pipelines reacting to 'recheck'
        recheck_pipelines = []
        for p in indep_pipelines:
            for ef in p.manager.event_filters:
                if [c for c in ef._comments if 'recheck' in c]:
                    recheck_pipelines.append(p)
                    break

        self.assertGreater(len(recheck_pipelines), 0)

        change = zuul.model.Change(self.sched.getProject('mediawiki/core'))
        change.branch = 'master'
        # Change already has received a code-review +2
        change.approvals = [{'type': 'Code-Review',
                             'description': 'Code Review',
                             'value': '2',
                             'by': {'email': 'someone@wikimedia.org'},
                             }]

        change_without_approvals = zuul.model.Change(
            self.sched.getProject('mediawiki/core'))
        change_without_approvals.branch = 'master'

        # They should reject CR+2 changes
        for p in recheck_pipelines:
            try:
                self.assertFalse(
                    p.manager.addChange(change),
                    "Independent pipeline '%s' must not process "
                    "a change having Code-Review +2" % (p.name)
                )
            except AssertionError, e:
                errors.append(str(e))
            try:
                self.assertTrue(
                    p.manager.addChange(change_without_approvals),
                    "Independent pipeline '%s' must accept a change "
                    "without any approval" % (p.name)
                )
            except AssertionError, e:
                errors.append(str(e))

        self.assertListEqual([], errors, "\n" + "\n".join(errors))

    def test_pipelines_trustiness(self):
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        # Untrusted user
        untrusted_event = zuul.model.TriggerEvent()
        untrusted_event.type = 'patchset-created'
        untrusted_event.account = {'email': 'untrusted@example.org'}
        untrusted_event.branch = change.branch
        self.assertFalse(test_manager.eventMatches(untrusted_event, change))

        # Trusted user
        trusted_event = zuul.model.TriggerEvent()
        trusted_event.type = 'patchset-created'
        trusted_event.account = {'email': 'jdoe@wikimedia.org'}
        trusted_event.branch = change.branch
        self.assertTrue(test_manager.eventMatches(trusted_event, change))

    def test_donationinterface_deployment_branch_filters(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/extensions/DonationInterface')
        change.branch = 'deployment'

        event = zuul.model.TriggerEvent()
        event.type = 'patchset-created'
        event.branch = change.branch

        jobs_tree = [t for (p, t) in
                     self.getPipeline('test').job_trees.iteritems()
                     if p.name == 'mediawiki/extensions/DonationInterface'][0]
        for job in jobs_tree.getJobs():
            if job.name.startswith('mwext-'):
                self.assertFalse(
                    job.changeMatches(change),
                    msg='%s should not trigger for branch %s' % (
                        job.name, change.branch)
                )

        self.assertTrue(test_manager.eventMatches(event, change))

    def test_donationinterface_docker_job_skips_on_mediawiki_core(self):
        repo = 'mediawiki/core'

        job = self.getJob(
            repo, 'test',
            'quibble-donationinterface-REL1_31-php70-docker')

        change = zuul.model.Change(repo)

        change.branch = 'master'

        self.assertFalse(job.changeMatches(change))

        change.branch = 'wmf/1.99.9-wmf.999'
        self.assertFalse(job.changeMatches(change))

        change.branch = 'REL1_42'
        self.assertFalse(job.changeMatches(change))

        # Only runs on mediawiki/core fundraising branch
        change.branch = 'fundraising/REL1_99'
        self.assertTrue(job.changeMatches(change))

    def test_rake_docker_files_filters(self):
        # FIXME: should be more generic
        jobs_tree = [t for (p, t) in
                     self.getPipeline('test').job_trees.iteritems()
                     if p.name == 'mediawiki/ruby/api'][0]
        rake_docker_job = [j for j in jobs_tree.getJobs()
                           if j.name.endswith('rake-docker')][0]

        def change_with_files(files):
            change = zuul.model.Change('mediawiki/ruby/api')
            change.branch = 'master'
            change.files.extend(files)
            return change

        cases = [
            (True, ['rakefile']),
            (True, ['tests/browser/Rakefile']),
            (True, ['foo/task.rb']),
            (True, ['module/spec/foo']),
            (True, ['Gemfile.lock']),
            (True, ['mediawiki_api.gemspec']),

            (False, ['foo.php']),
        ]
        errors = []
        for (expect, files) in cases:
            change = change_with_files(files)
            try:
                if expect:
                    self.assertTrue(
                        rake_docker_job.changeMatches(change),
                        'rake-docker should run with files: %s' % files)
                else:
                    self.assertFalse(
                        rake_docker_job.changeMatches(change),
                        'rake-docker should NOT run with files: %s' % files)
            except AssertionError, e:
                errors.append(str(e))

        self.assertListEqual([], errors)

    def test_debian_glue_triggers_for_debian_directory_changes(self):
        job = self.getJob('blubber', 'test', 'debian-glue')

        change = zuul.model.Change('blubber')
        change.files.extend(['debian/changelog'])

        self.assertTrue(job.changeMatches(change))

    def test_debian_glue_filtered_for_non_debian_changes(self):
        job = self.getJob('blubber', 'test', 'debian-glue')

        change = zuul.model.Change('blubber')
        change.files.extend(['README'])

        self.assertFalse(job.changeMatches(change))

    def test_l10nbot_patchets_are_ignored(self):
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        l10n_event = zuul.model.TriggerEvent()
        l10n_event.type = 'patchset-created'
        l10n_event.account = {'email': 'l10n-bot@translatewiki.net'}
        l10n_event.branch = change.branch

        self.assertFalse(test_manager.eventMatches(l10n_event, change),
                         'l10-bot should not enter %s pipeline' %
                         test_manager.pipeline.name)

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

    def test_trusted_cr_vote_tests_untested_change(self):
        test_manager = self.getPipeline('test').manager

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'
        change.approvals = [
            {'description': 'Verified',
             'type': 'VRFY',
             'value': '1',
             'by': {'username': 'jenkins-bot'},
             },
            {'description': 'Code-Review',
             'type': 'CRVW',
             'value': '1',
             'by': {'email': 'jdoe@wikimedia.org'},
             },
        ]

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.account = {'email': 'untrusted@example.org'}
        event.approvals = [
            {'description': 'Code-Review',
             'type': 'CRVW',
             'value': '1',
             'by': {'email': 'unstrusted@example.org'},
             },
        ]
        event.branch = change.branch
        self.assertFalse(test_manager.eventMatches(event, change))

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.account = {'email': 'jdoe@wikimedia.org'}
        event.approvals = [
            {'description': 'Code-Review',
             'type': 'CRVW',
             'value': '1',
             },
        ]
        event.branch = change.branch
        self.assertTrue(test_manager.eventMatches(event, change))

        change.approvals = [{
            'description': 'Verified',
            'type': 'VRFY',
            'value': '-1',
            'by': {'username': 'jenkins-bot'},
        }]
        self.assertFalse(
            test_manager.eventMatches(event, change),
            'Verified -1 prevents CR+1 from triggering tests'
        )

        change.approvals[0]['value'] = 2
        self.assertFalse(
            test_manager.eventMatches(event, change),
            'Verified +2 prevents CR+1 from triggering tests'
        )

    def test_gated_extensions_lists_are_in_sync(self):
        self.longMessage = True

        global_env = {}
        execfile(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../zuul/parameter_functions.py'),
            global_env)
        tarballextensions = set(global_env['tarballextensions'])
        gatedextensions = set(global_env['gatedextensions'])

        allextensions = tarballextensions.union(gatedextensions)

        # Grab projects having the gate job 'wmf-quibble-*'
        gated_in_zuul = set([
            ext_name[len('mediawiki/extensions/'):]  # extension basename
            for (ext_name, pipelines) in self.getProjectsDefs().iteritems()
            if ext_name.startswith('mediawiki/extensions/')
            and 'wmf-quibble-vendor-mysql-hhvm-docker'
                in pipelines.get('test', {})
        ])

        self.assertSetEqual(
            gated_in_zuul, allextensions,
            msg='Zuul projects triggering gate jobs (first set) and '
            'dependencies list in zuul/parameter_functions.py (second set) '
            'must be equals.\n'
            'In Zuul: apply the template extension-gate\n'
            'In JJB: add extension to "gatedextensions"')

    def test_pipelines_have_report_action_to_gerrit(self):
        not_reporting = ['post', 'publish']
        required_actions = ['success', 'failure']
        reporting_pipelines = [
            p for p in self.getPipelines()
            if p.name not in not_reporting]

        for pipeline in reporting_pipelines:
            for action in required_actions:
                reporters = pipeline.__getattribute__(action + '_actions')
                self.assertTrue(
                    # At least one reporter is to Gerrit
                    any([isinstance(reporter, GerritReporter)
                         for reporter in reporters]
                        ),
                    'Pipeline %s must have a GerritReporter on %s got %s' % (
                        pipeline.name, action, reporters)
                )

    # Gerrit review command tends to change between release
    #
    # The Zuul layout configuration must have an empty list of parameters {}
    # and should not vote on a closed change.
    # T153737
    def test_postmerge_gerrit_review_command(self):
        pipe = self.getPipeline('postmerge')
        # Pick the first Gerrit success reporter
        gerrit_reporter = [r for r in pipe.success_actions
                           if isinstance(r, GerritReporter)][0]
        self.assertEquals({}, gerrit_reporter.reporter_config)

        gerrit = GerritConnection('fake_gerrit',
                                  {'server': 'localhost', 'user': 'john'})
        # Fake ssh (stdout, stderr) so the command is returned by review()
        gerrit._ssh = lambda x: ['', x]
        cmd = gerrit.review('some/project', '12345,42', 'hello world')
        self.longMessage = True
        self.assertEquals(
            'gerrit review --project some/project '
            '--message "hello world" 12345,42',
            cmd,
            'gerrit review command does not match Gerrit 2.13 expectation')

    def test_gate_has_a_mediawiki_queue(self):
        gate = self.getPipeline('gate-and-submit')
        queue_names = [q.name for q in gate.queues]
        self.assertIn(
            'mediawiki', queue_names,
            'gate-and-submit must have a queue named "mediawiki"')

    def test_only_mediawiki_projects_in_mediawiki_gate(self):

        def _mw_filter(zuul_project, is_mw):
            p_name = zuul_project.name
            if (
                p_name.startswith('mediawiki/extensions/')
                or p_name.startswith('mediawiki/skins/')
                or p_name == 'mediawiki/vendor'
                or p_name == 'mediawiki/core'
                or p_name == 'data-values/value-view'
            ):
                return is_mw
            return not is_mw

        def isMediawiki(zuul_project):
            return _mw_filter(zuul_project, is_mw=True)

        def isNotMediawiki(zuul_project):
            return _mw_filter(zuul_project, is_mw=False)

        gate = self.getPipeline('gate-and-submit')
        mw_queue = [q for q in gate.queues if q.name == 'mediawiki'][0]

        # Gather a set of jobs for MediaWiki repositories as defined in the
        # layout, ie before the projects are merged in the change queue.
        mw_defined_jobs = set()
        for project in filter(isMediawiki, mw_queue.projects):
            mw_defined_jobs.update([
                j.name for j in gate.getJobTree(project).getJobs()
                ])

        # noop job does not merge queues on Wikimedia setup
        # https://review.openstack.org/#/c/361505/2
        mw_defined_jobs.discard('noop')

        errors = {}
        # Projects that are not supposed to be in the 'mediawiki' queue. Either
        # because they share a job with a mediawiki repository either directly
        # or transitively.
        unintended = filter(isNotMediawiki, mw_queue.projects)
        for project in unintended:
            project_jobs = {j.name for j in gate.getJobTree(project).getJobs()}
            unintended_jobs = list(project_jobs.intersection(mw_defined_jobs))
            if unintended_jobs:
                errors[project.name] = unintended_jobs
            # Else project got merged in the change queue transitively, ie
            # because it shares jobs with an other unintended project.

        self.maxDiff = None
        self.longMessage = True
        self.assertDictEqual(
            {}, errors, "\nNon MediaWiki projects must not have jobs "
                        "in common with the mediawiki queue.")

    def test_mwcore_switch_to_quibble(self):
        expected_test = {
            # It is not triggered for the master branch:
            'quibble-donationinterface-REL1_31-php70-docker': False,

            'mediawiki-core-jsduck-docker': True,
            'mediawiki-core-php70-phan-docker': True,
            'mediawiki-quibble-composer-mysql-php70-docker': True,
            'mediawiki-quibble-vendor-mysql-php70-docker': True,
            'mediawiki-quibble-vendor-mysql-hhvm-docker': False,
            'mediawiki-quibble-composertest-php70-docker': True,
            'release-quibble-vendor-mysql-hhvm-docker': False,
            'release-quibble-vendor-mysql-php55-docker': False,
            'release-quibble-vendor-mysql-php70-docker': False,
            'wmf-quibble-vendor-mysql-hhvm-docker': False,
            'wmf-quibble-core-vendor-mysql-hhvm-docker': True,
            'mwgate-npm-node-6-docker': True,
        }
        expected_gate = {
            'mediawiki-core-jsduck-docker': True,
            'mediawiki-core-php70-phan-docker': True,
            'mediawiki-quibble-composer-mysql-php70-docker': True,
            'mediawiki-quibble-vendor-mysql-php72-docker': True,
            'mediawiki-quibble-vendor-mysql-php71-docker': True,
            'mediawiki-quibble-vendor-mysql-php70-docker': True,
            'mediawiki-quibble-vendor-mysql-php55-docker': False,
            'mediawiki-quibble-vendor-mysql-hhvm-docker': True,
            'mediawiki-quibble-composertest-php70-docker': True,
            'mediawiki-quibble-vendor-sqlite-php72-docker': True,
            'mediawiki-quibble-vendor-postgres-php72-docker': True,
            'release-quibble-vendor-mysql-hhvm-docker': False,
            'release-quibble-vendor-mysql-php55-docker': False,
            'release-quibble-vendor-mysql-php70-docker': False,
            'release-quibble-vendor-mysql-php71-docker': False,
            'release-quibble-vendor-mysql-php72-docker': False,
            'wmf-quibble-vendor-mysql-hhvm-docker': False,
            'wmf-quibble-vendor-mysql-php70-docker': False,
            'wmf-quibble-vendor-mysql-php71-docker': False,
            'wmf-quibble-vendor-mysql-php72-docker': False,
            'wmf-quibble-core-vendor-mysql-hhvm-docker': True,
            'wmf-quibble-core-vendor-mysql-php72-docker': True,
            'mwgate-npm-node-6-docker': True,
        }

        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'
        change.files.extend(['foo.php', 'composer.json'])

        job_tree = [t for (p, t) in
                    self.getPipeline('test').job_trees.iteritems()
                    if p.name == 'mediawiki/core'][0]
        test_jobs = job_tree.getJobs()
        job_tree = [t for (p, t) in
                    self.getPipeline('gate-and-submit').job_trees.iteritems()
                    if p.name == 'mediawiki/core'][0]
        gate_jobs = job_tree.getJobs()

        for job in test_jobs:
            self.assertEqual(
                expected_test[job.name],
                job.changeMatches(change),
                'test: %s expected match == %s '
                'but change matching returned %s' % (
                    job.name, expected_test[job.name],
                    job.changeMatches(change))
                )
        for job in gate_jobs:
            self.assertEqual(
                expected_gate[job.name],
                job.changeMatches(change),
                'gate: %s expected match == %s '
                'but change matching returned %s' % (
                    job.name, expected_gate[job.name],
                    job.changeMatches(change))
                )

    def test_quibble_71_72_jobs_are_skipped_on_fundraising_branches(self):
        change = zuul.model.Change('mediawiki/core')
        change.branch = 'fundraising/REL1_31'

        job = self.getJob(
            'mediawiki/core',
            'gate-and-submit',
            'mediawiki-quibble-vendor-mysql-php71-docker')
        self.assertFalse(
            job.changeMatches(change),
            'Quibble must be skipped on fundraising branches')

        wmf_job = self.getJob(
            'mediawiki/core',
            'gate-and-submit',
            'wmf-quibble-vendor-mysql-php71-docker')
        self.assertFalse(
            wmf_job.changeMatches(change),
            'WMF Quibble job must be skipped on fundraising branches')

    def test_wmf_quibble_for_extensions(self):
        wmf_quibble_job = self.getJob(
            'mediawiki/extensions/AbuseFilter',
            'gate-and-submit',
            'wmf-quibble-vendor-mysql-php70-docker')
        release_job = self.getJob(
            'mediawiki/extensions/AbuseFilter',
            'gate-and-submit',
            'release-quibble-vendor-mysql-php70-docker')

        change = zuul.model.Change('mediawiki/extensions/AbuseFilter')

        # wmf-quibble jobs target master and wmf branches
        change.branch = 'wmf/1.99.9-wmf.999'
        self.assertTrue(
            wmf_quibble_job.changeMatches(change),
            'wmf-quibble jobs run on wmf branches')
        self.assertFalse(
            release_job.changeMatches(change),
            'release job is not for wmf branches')

        change.branch = 'master'
        self.assertTrue(
            wmf_quibble_job.changeMatches(change),
            'wmf-quibble jobs run on master branch')
        self.assertFalse(
            release_job.changeMatches(change),
            'release job is not for master branch')

        # We run it on feature branches as well:
        change.branch = 'feature'
        self.assertTrue(
            wmf_quibble_job.changeMatches(change),
            'wmf-quibble jobs run on feature branch')
        self.assertFalse(
            release_job.changeMatches(change),
            'release job is not for feature branch')

        # But not the release branches
        change.branch = 'REL1_42'
        self.assertFalse(
            wmf_quibble_job.changeMatches(change),
            'wmf-quibble jobs are not for REL branches')
        self.assertTrue(
            release_job.changeMatches(change),
            'release jobs run on REL branches')

    def test_gated_extension_run_tests_on_rel_branch(self):
        repo = 'mediawiki/extensions/Translate'
        release_job = self.getJob(
            repo, 'test',
            'release-quibble-vendor-mysql-hhvm-docker')

        change = zuul.model.Change(repo)

        change.branch = 'REL1_42'
        self.assertTrue(release_job.changeMatches(change))

    def test_postgres_sqlite_job(self):
        repo = 'mediawiki/core'
        job = self.getJob(
            repo, 'gate-and-submit',
            'mediawiki-quibble-vendor-postgres-php72-docker')

        change = zuul.model.Change(repo)

        # Doesn't run on wmf/
        change.branch = 'wmf/1.31.0-wmf.28'
        self.assertFalse(job.changeMatches(change))

        # Doesn't run on fundraising/
        change.branch = 'fundraising/REL1_31'
        self.assertFalse(job.changeMatches(change))

        # Doesn't run on REL1_31
        change.branch = 'REL1_31'
        self.assertFalse(job.changeMatches(change))

        # Runs on master
        change.branch = 'master'
        self.assertTrue(job.changeMatches(change))

        # Runs on REL1_32
        change.branch = 'REL1_32'
        self.assertTrue(job.changeMatches(change))

    def test_gated_extension_run_tests_on_feature_branch(self):
        repo = 'mediawiki/extensions/CirrusSearch'
        release_job = self.getJob(
            repo, 'test',
            'wmf-quibble-vendor-mysql-hhvm-docker')

        change = zuul.model.Change(repo)

        change.branch = 'es6'
        self.assertTrue(release_job.changeMatches(change))

    def test_gated_extension_behavior(self):
        repo = 'mediawiki/extensions/Translate'

        wmf_quibble_job = self.getJob(
            repo, 'gate-and-submit',
            'wmf-quibble-vendor-mysql-php70-docker')
        release_job = self.getJob(
            repo, 'gate-and-submit',
            'release-quibble-vendor-mysql-php70-docker')

        change = zuul.model.Change(repo)

        change.branch = 'master'
        self.assertTrue(wmf_quibble_job.changeMatches(change))
        self.assertFalse(release_job.changeMatches(change))

        change.branch = 'wmf/1.99.9-wmf.999'
        self.assertTrue(wmf_quibble_job.changeMatches(change))
        self.assertFalse(release_job.changeMatches(change))

        change.branch = 'feature'
        self.assertTrue(wmf_quibble_job.changeMatches(change))
        self.assertFalse(release_job.changeMatches(change))

        change.branch = 'REL1_42'
        self.assertFalse(wmf_quibble_job.changeMatches(change))
        self.assertTrue(release_job.changeMatches(change))

    def test_php71_test_jobs_are_skipped_for_phptags_extension(self):
        repo = 'mediawiki/extensions/PhpTags'

        change = zuul.model.Change(repo)
        change.branch = 'master'

        php71_job = self.getJob(repo, 'gate-and-submit',
                                'quibble-vendor-mysql-php71-docker')
        self.assertFalse(
            php71_job.changeMatches(change),
            'php7.1 test job must not run for PhpTags - T188585')

        hhvm_job = self.getJob(repo, 'gate-and-submit',
                               'quibble-vendor-mysql-hhvm-docker')
        self.assertTrue(hhvm_job.changeMatches(change))
        hhvm_job = self.getJob(repo, 'gate-and-submit',
                               'quibble-vendor-mysql-php70-docker')
        self.assertTrue(hhvm_job.changeMatches(change))
