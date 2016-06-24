# Verify Wikimedia Zuul scheduler functionalities
#
# Copyright (c) 2014 - Antoine "hashar" Musso
# Copyright (c) 2014 - Wikimedia Foundation Inc.

import ConfigParser
import copy
import re
import os
import unittest

import yaml
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

        cls.sched = zuul.scheduler.Scheduler()
        # Reporters and Triggers are registered by zuul-server, not the
        # Scheduler class:
        cls.sched.registerTrigger(FakeTrigger(), 'gerrit')
        cls.sched.registerTrigger(FakeTrigger(), 'timer')
        cls.sched.registerTrigger(FakeTrigger(), 'zuul')
        cls.sched._doReconfigureEvent(ReconfigureEvent(cfg))

    @classmethod
    def tearDownClass(cls):
        cls.sched.exit()

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
        self.assertTrue(
            any([job for job in definition
                 if job.startswith(('composer', 'composer-'))]),
            'Project %s pipeline %s must have either '
            'composer-validate or a composer-* job'
            % (name, pipeline))

    def assertProjectHasPhplint(self, name, definition, pipeline):
        self.assertTrue(
            any([job for job in definition
                 if job.endswith(('php53lint', 'php55lint')) or
                 job.startswith('composer-')]),
            'Project %s pipeline %s must have either '
            'phplint or a composer-* job'
            % (name, pipeline))

    def assertProjectHasPhp53TestAnd55(self, name, definition, pipeline):
        has_53 = False
        for job in definition:
            if 'testextension-php53' in job:
                has_53 = True
                break
        if not has_53:
            self.assertFalse(has_53)
            return
        for job in definition:
            if 'testextension-php55' in job:
                self.assertTrue(True)
                return

        self.assertTrue(False, 'Project %s pipeline %s must have a '
                        'php55 test job' % (name, pipeline))

    def test_repos_have_required_jobs(self):
        repos = {
            'mediawiki/core$': [
                self.assertProjectHasComposerValidate,
                self.assertProjectHasPhplint
            ],
            'mediawiki/extensions/\w+$': [
                self.assertProjectHasComposerValidate,
                self.assertProjectHasPhplint,
                self.assertProjectHasPhp53TestAnd55
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
            if 'check-only' in project_def.keys():
                requirements.add('check-only')
            elif 'check-voter' in project_def.keys():
                # Skins uses a different check pipeline
                requirements.add('check-voter')
            else:
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
                # Weird edge case:
                or project == 'analytics/kraken'
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

    def test_projects_in_check_only_are_not_in_test_pipeline(self):
        self.assertPipelinesDoNotOverlap(
            'check-only', 'test',
            msg="check-only is only for projects not having entries in the "
                "test pipeline. Move the jobs to 'check' pipeline instead.")

    def test_projects_in_check_voter_are_not_in_test_pipeline(self):
        self.assertPipelinesDoNotOverlap(
            'check-voter', 'test',
            msg="check-voter is only for projects not having entries in "
                "the test pipeline and for which the repository lacks tests. "
                "Move jobs from check-voter to check pipeline")

    def test_valid_jobs_in_check_pipelines(self):
        check_pipelines = [p.name for p in self.getPipelines()
                           if p.name.startswith('check')]

        # We expect check pipelines to have no unsafe jobs
        expected = {k: {} for k in check_pipelines}
        # Map of pipelines -> projects -> unsafe jobs
        actual = copy.deepcopy(expected)

        # List of jobs allowed in check* pipelines
        safe_jobs = [
            '(php5[35]|json|yaml)lint',
            'jshint',
            '.*-(jshint|jsonlint)',
            '.*-(js|shell|php5[35]|)lint',
            '(pp|erb)lint-HEAD',
            '.*-(tabs|typos)',
            '.*-puppet-validate',
            '.*-puppetlint-strict',
            '.*-whitespaces',
            'noop',
            'composer-validate',
            'composer-package-validate',
            'fail-archived-repositories',
            'tox-jessie',
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

    def test_recheck_comment_untrusted_user_with_code_review(self):
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')

        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: -Code-Review\n\nrecheck'
        event.account = {'email': 'untrusted@example.org'}
        self.assertFalse(test_manager.eventMatches(event, change))

    def test_recheck_with_code_review_vote_removed(self):
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')
        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: -Code-Review\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_with_verified_vote_removed(self):
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')
        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: -Verified\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        self.assertFalse(test_manager.eventMatches(event, change))

    def test_recheck_with_code_review_vote_plus_one(self):
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')
        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Code-Review+1\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_with_code_review_vote_plus_two(self):
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')
        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Code-Review+2\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_with_code_review_vote_minus_one(self):
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')
        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Code-Review-1\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_with_code_review_vote_minus_two(self):
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')
        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Code-Review-2\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        self.assertTrue(test_manager.eventMatches(event, change))

    def test_recheck_with_verified_vote_minus_two(self):
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')
        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Verified-2\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        self.assertFalse(test_manager.eventMatches(event, change))

    def test_recheck_with_verified_vote_minus_one(self):
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')
        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Verified-1\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        self.assertFalse(test_manager.eventMatches(event, change))

    def test_recheck_with_verified_vote_plus_one(self):
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')
        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Verified+1\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
        self.assertFalse(test_manager.eventMatches(event, change))

    def test_recheck_with_verified_vote_plus_2(self):
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')
        event = zuul.model.TriggerEvent()
        event.type = 'comment-added'
        event.comment = 'Patch Set 1: Verified+2\n\nrecheck'
        event.account = {'email': 'jdoe@wikimedia.org'}
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

    def test_smashpig_deployment_branch_filters(self):
        # Since SmashPig override a generic skip-if set by ^.*php53.*$
        # Make sure it is properly honored.
        test_manager = self.getPipeline('test').manager
        event = zuul.model.TriggerEvent()
        event.type = 'patchset-created'

        change = zuul.model.Change('wikimedia/fundraising/SmashPig')
        change.branch = 'deployment'

        jobs_tree = [t for (p, t) in
                     self.getPipeline('test').job_trees.iteritems()
                     if p.name == 'wikimedia/fundraising/SmashPig'][0]
        for job in jobs_tree.getJobs():
            if job.name in ['composer-php53', 'composer-hhvm-trusty']:
                self.assertFalse(
                    job.changeMatches(change),
                    msg='%s should not trigger for branch %s' % (
                        job.name, change.branch)
                )

        self.assertTrue(test_manager.eventMatches(event, change))

    # Make sure rake-jessie is properly filtered
    # https://phabricator.wikimedia.org/T105178
    def test_mediawiki_core_rake_filters(self):
        test_manager = self.getPipeline('test').manager
        jobs_tree = [t for (p, t) in
                     self.getPipeline('test').job_trees.iteritems()
                     if p.name == 'mediawiki/core'][0]
        rake_job = [j for j in jobs_tree.getJobs()
                    if j.name == 'rake-jessie'][0]

        def change_for_branch(branch_name):
            """Return a change against branch_name branch"""
            change = zuul.model.Change('mediawiki/core')
            change.branch = branch_name
            change.files.append('Gemfile.lock')
            return change

        event = zuul.model.TriggerEvent()
        event.type = 'patchset-created'
        event.account = {'email': 'johndoe@wikimedia.org'}

        for allowed_branch in ['master', 'REL1_25', 'REL1_26']:
            change = change_for_branch(allowed_branch)
            self.assertTrue(test_manager.eventMatches(event, change))
            self.assertTrue(rake_job.changeMatches(change),
                            'mediawiki/core rake job must run on %s'
                            % allowed_branch)

        for blacklisted_branch in ['REL1_23', 'REL1_24',
                                   'fundraising/REL1_42']:
            change = change_for_branch(blacklisted_branch)
            self.assertTrue(test_manager.eventMatches(event, change))
            self.assertFalse(rake_job.changeMatches(change),
                             'mediawiki/core rake job must NOT run on %s'
                             % blacklisted_branch)

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

    def test_trusted_cr_vote_tests_untested_change(self):
        test_manager = self.getPipeline('test').manager
        change = zuul.model.Change('mediawiki/core')
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
        self.assertTrue(test_manager.eventMatches(event, change))

    def test_gated_extensions_are_both_in_jjb_and_zuul(self):
        self.longMessage = True

        # Grab deps from the JJB template mediawiki-extensions-{phpflavor}
        jjb_mw_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../jjb/mediawiki.yaml')
        with open(jjb_mw_file, 'r') as f:
            jjb = yaml.load(f)

        mw_project = next(entry['project'] for entry in jjb
                          if 'project' in entry
                          and entry['project'].get('name') == 'mediawiki-core')
        jjb_gate_template = next(
            job['mediawiki-extensions-{phpflavor}']
            for job in mw_project['jobs']
            if isinstance(job, dict)
            and job.keys()[0] == 'mediawiki-extensions-{phpflavor}')
        # List of extensions basenames. Space separted in the YAML definition.
        jjb_deps = set(jjb_gate_template['dependencies'].rstrip().split(' '))

        # Grab projects having the gate job 'mediawiki-extensions-hhvm'
        gated_in_zuul = set([
            ext_name[len('mediawiki/extensions/'):]  # extension basename
            for (ext_name, pipelines) in self.getProjectsDefs().iteritems()
            if ext_name.startswith('mediawiki/extensions/')
            and 'mediawiki-extensions-hhvm' in pipelines.get('test', {})
        ])

        self.assertSetEqual(
            gated_in_zuul, jjb_deps, msg='Zuul projects triggering gate jobs '
            '(first set) and dependencies list in JJB (second set) must be '
            'equals.\n'
            'In Zuul: apply the template extension-gate\n'
            'In JJB: add extension to "gatedextensions"')
