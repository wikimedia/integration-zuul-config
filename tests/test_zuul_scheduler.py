# Verify Wikimedia Zuul scheduler functionalities
#
# Copyright (c) 2014 - Antoine "hashar" Musso
# Copyright (c) 2014 - Wikimedia Foundation Inc.

import ConfigParser
import copy
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
        # composer-validate
        # composer-validate-package
        # composer-test-(zend|hhvm)
        # mwgate-composer-validate
        self.assertTrue(
            any([job for job in definition
                 if (
                     job.startswith(('composer', 'mwgate-composer'))
                     or job.startswith('mediawiki-extensions-')
                     or (job.startswith('mwext-testextension-')
                         and 'non-voting' not in job)
                 )]),
            'Project %s pipeline %s must have either '
            'composer-validate or a composer-* job'
            'has: %s'
            % (name, pipeline, definition))

    def assertTestextensionAndNoComposerTest(self, name, definition, pipeline):
        # XXX
        if pipeline == 'gate-and-submit':
            return

        hasVotingTests = any([
            job for job in definition
            if job.startswith(
                ('mwext-testextension-', 'mediawiki-extensions-'))
            and 'non-voting' not in job
            ])
        hasComposerTest = any([
            job for job in definition
            if job.startswith('mwgate-composer-')])
        self.assertTrue(
            not (hasVotingTests and hasComposerTest),
            'Project %s pipeline %s has mwext-testextension-* jobs '
            'which runs composer test. mwgate-composer-* are not needed. '
            'Has: %s'
            % (name, pipeline, definition))

    def assertProjectHasPhplint(self, name, definition, pipeline):
        self.assertTrue(
            any([job for job in definition
                 if job.endswith(('php55lint')) or
                 job.endswith(('php56lint')) or
                 job.startswith('mediawiki-extensions-') or
                 job.startswith(('composer-', 'mwgate-composer'))]),
            'Project %s pipeline %s must have either '
            'phplint or a composer-* job'
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
                 if job.startswith('mwskin-testskin')]),
            'Project %s pipeline %s must have job '
            'starting with mwskin-testskin'
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

    def test_repos_have_required_jobs(self):
        repos = {
            'mediawiki/core$': [
                self.assertProjectHasComposerValidate,
                self.assertProjectHasPhplint
            ],
            'mediawiki/extensions/\w+$': [
                self.assertProjectHasComposerValidate,
                self.assertProjectHasPhplint,
                self.assertProjectHasPhp55Test,
                self.assertTestextensionAndNoComposerTest
            ],
            'mediawiki/skins/': [
                self.assertProjectHasComposerValidate,
                self.assertProjectHasPhplint,
                self.assertProjectHasSkinTests,
                self.assertProjectHasNoExtensionTests
            ],
            'mediawiki/vendor$': [
                self.assertProjectHasComposerValidate,
                self.assertProjectHasPhplint
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
            if 'gate-and-submit' in project_def \
                    and 'fail-archived-repositories' \
                        in project_def['gate-and-submit']:
                continue

            # Pipelines that must be set
            requirements = set()
            requirements.add('gate-and-submit')
            for default_requirement in ['check', 'test']:
                requirements.add(default_requirement)
                self.assertIn(default_requirement, project_def.keys(),
                              'Project %s must have a %s pipeline'
                              % (project_name, default_requirement))

            # Validate the pipeline has the proper jobs
            for req_pipeline in requirements:
                for func in assertions:
                    func(project_name,
                         project_def[req_pipeline], req_pipeline)

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

    def test_projects_have_only_one_check_pipeline(self):
        dupe_check = {}
        for (project, pipelines) in self.getProjectsPipelines().iteritems():
            check_pipelines = [p for p in pipelines if p.startswith('check')]
            if len(check_pipelines) > 1:
                dupe_check[project] = check_pipelines

        self.longMessage = True
        self.maxDiff = None

        self.assertEquals(
            {}, dupe_check,
            msg="Projects can only be in a single check pipeline")

    def assertPipelinesDoNotOverlap(self, pipeline_name_1, pipeline_name_2,
                                    msg=None):
        first = set(self.getPipelineProjectsNames(pipeline_name_1))
        second = set(self.getPipelineProjectsNames(pipeline_name_2))

        self.longMessage = True
        self.maxDiff = None
        self.assertEqual(set(), first & second, msg)

    def test_valid_jobs_in_check_pipelines(self):
        check_pipelines = [p.name for p in self.getPipelines()
                           if p.name.startswith('check')]

        # We expect check pipelines to have no unsafe jobs
        expected = {k: {} for k in check_pipelines}
        # Map of pipelines -> projects -> unsafe jobs
        actual = copy.deepcopy(expected)

        # List of jobs allowed in check* pipelines
        safe_jobs = [
            '(php(55|56|70)|yaml)lint',
            '.*-(js|shell|php(55|56|70)|)lint',
            '.*-(tabs|typos)',
            '.*-whitespaces',
            'noop',
            '(?:mwgate-)?composer-validate',
            'composer-package-validate',
            'fail-archived-repositories',
            '.*tox-docker',
            'commit-message-validator',
        ]
        safe_jobs_re = re.compile('^(' + '|'.join(safe_jobs) + ')$')

        all_defs = self.getProjectsDefs()
        for (project_name, defs) in all_defs.iteritems():
            for (pipeline, jobs) in defs.iteritems():
                if not pipeline.startswith('check'):
                    continue
                unsafe_jobs = [j for j in jobs
                               if not re.match(safe_jobs_re, j)]
                if unsafe_jobs:
                    actual[pipeline].update({project_name: unsafe_jobs})

        self.maxDiff = None
        self.longMessage = True

        self.assertEquals(expected, actual,
                          "No project have unsafe jobs in check* pipelines")

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

    def test_pipelines_trustiness(self):
        check_manager = self.getPipeline('check').manager
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        # Untrusted user
        untrusted_event = zuul.model.TriggerEvent()
        untrusted_event.type = 'patchset-created'
        untrusted_event.account = {'email': 'untrusted@example.org'}
        untrusted_event.branch = change.branch
        self.assertTrue(check_manager.eventMatches(untrusted_event, change))
        self.assertFalse(test_manager.eventMatches(untrusted_event, change))

        # Trusted user
        trusted_event = zuul.model.TriggerEvent()
        trusted_event.type = 'patchset-created'
        trusted_event.account = {'email': 'jdoe@wikimedia.org'}
        trusted_event.branch = change.branch
        self.assertFalse(check_manager.eventMatches(trusted_event, change))
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

    def test_l10nbot_patchets_are_ignored(self):
        managers = [self.getPipeline(p).manager
                    for p in ['check', 'test']]
        change = zuul.model.Change('mediawiki/core')
        change.branch = 'master'

        l10n_event = zuul.model.TriggerEvent()
        l10n_event.type = 'patchset-created'
        l10n_event.account = {'email': 'l10n-bot@translatewiki.net'}
        l10n_event.branch = change.branch

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
        gatedextensions = set(global_env['gatedextensions'])

        # Grab projects having the gate job 'mediawiki-extensions-hhvm'
        gated_in_zuul = set([
            ext_name[len('mediawiki/extensions/'):]  # extension basename
            for (ext_name, pipelines) in self.getProjectsDefs().iteritems()
            if ext_name.startswith('mediawiki/extensions/')
            and 'mediawiki-extensions-hhvm-jessie' in pipelines.get('test', {})
        ])

        self.assertSetEqual(
            gated_in_zuul, gatedextensions,
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
            'composer-package-validate': True,
            'mediawiki-core-jsduck-docker': True,
            'mediawiki-core-php55lint': True,
            'mediawiki-core-php70-phan-docker': True,
            'mediawiki-extensions-hhvm-jessie': True,
            'mediawiki-extensions-qunit-jessie': True,
            'mediawiki-phpunit-hhvm-jessie': True,
            'quibble-composer-mysql-php70-docker': True,
            'quibble-vendor-mysql-php70-docker': True,

            # Migrated on master
            'mediawiki-core-phpcs-docker': False,
            'mediawiki-core-qunit-selenium-jessie': False,
            'mediawiki-core-npm-node-6-docker': False,
            'mediawiki-core-php70lint': False,
        }
        expected_gate = {
            'composer-package-validate': True,
            'mediawiki-core-jsduck-docker': True,
            'mediawiki-core-php55lint': True,
            'mediawiki-core-php70-phan-docker': True,
            'mediawiki-extensions-hhvm-jessie': True,
            'mediawiki-extensions-php55-jessie': True,
            'mediawiki-extensions-php70-jessie': True,
            'mediawiki-extensions-qunit-jessie': True,
            'mediawiki-phpunit-hhvm-jessie': True,
            'mediawiki-phpunit-php55-jessie': True,
            'quibble-composer-mysql-php70-docker': True,
            'quibble-vendor-mysql-php70-docker': True,

            # Migrated on master
            'mediawiki-core-npm-node-6-docker': False,
            'mediawiki-core-php70lint': False,
            'mediawiki-core-phpcs-docker': False,
            'mediawiki-core-qunit-selenium-jessie': False,
            'mediawiki-phpunit-php70-composer-jessie': False,
            'mediawiki-phpunit-php70-jessie': False,
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

        change.branch = 'REL1_30'
        for job in test_jobs:
            if job.name.startswith('quibble'):
                self.assertFalse(
                    job.changeMatches(change),
                    'Quibble must not trigger on %s' % change.branch)
            else:
                self.assertTrue(
                    job.changeMatches(change),
                    '%s must trigger on %s' % (job.name, change.branch))
