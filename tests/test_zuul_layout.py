# Parse Zuul layout.yaml file
#
# Copyright (c) 2016 - Antoine "hashar" Musso
# Copyright (c) 2016 - Wikimedia Foundation Inc.

import os
import unittest

import yaml

from fakes import FakeJob

dependencies = None  # defined for flake8
set_parameters = None  # defined for flake8

# Import function
execfile(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../zuul/parameter_functions.py'))


class TestZuulLayout(unittest.TestCase):
    """
    Tests solely asserting on the Zuul YAML configuration.

    Notably expansion of templates are not available which is provied by the
    scheduler and tested via test_zuul_scheduler.py
    """

    layout = None

    @classmethod
    def setUpClass(cls):
        wmf_zuul_layout = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../zuul/layout.yaml')
        with open(wmf_zuul_layout, 'r') as f:
            cls.layout = yaml.safe_load(f)

    def getExtSkinRepos(self):
        projects = []
        for project in self.layout['projects']:
            if not project['name'].startswith((
                    'mediawiki/skins', 'mediawiki/extensions')):
                continue
            if len(project['name'].split('/')) != 3:
                # Skip sub repositories
                continue
            projects.append(project)

        return projects

    def getProjectTemplates(self):
        templates = {}
        for project_template in self.layout['project-templates']:
            name = project_template['name']
            del(project_template['name'])
            templates[name] = project_template
        return templates

    def test_mediawiki_ext_skins_have_test_templates(self):
        one_of_templates = (
            'archived',
            'extension-broken',
            'extension-unittests',
            'extension-quibble',
            'skin-tests',
            'skin-quibble',
            'extension-gate',
            'quibble-vendor',
            )
        # Special cases for Fundraising reasons
        special_cases = (
            'mediawiki/extensions/DonationInterface',
            'mediawiki/extensions/FundraisingEmailUnsubscribe'
            )

        errors = []
        for project in self.getExtSkinRepos():

            if project['name'] in special_cases:
                continue

            try:
                has_extension_unittests = any([
                    template['name'].startswith(one_of_templates)
                    for template in project.get('template', {})
                    ])
                self.assertTrue(
                    has_extension_unittests,
                    'Project %s in Zuul lacks an extension-unittests* '
                    'template' % project['name'])
            except AssertionError, e:
                errors.append(str(e))

        self.maxDiff = None
        self.assertListEqual([], errors)

    def test_gated_extensions_have_quibble_regular_template(self):
        errors = []
        for project in self.getExtSkinRepos():
            try:
                if 'template' not in project:
                    continue

                templates = [template['name']
                             for template in project.get('template')]
                if 'extension-gate' not in templates:
                    continue

                # Extract singular 'extension' or 'skin'
                kind = project['name'].split('/')[1][:-1]

                if 'extension-quibble-only-selenium' in templates:
                    self.assertIn(
                        'extension-quibble-noselenium',
                        templates,
                        'Must have both noselenium and only-selenium'
                    )
                    self.assertNotIn('extension-quibble', templates)
                else:
                    if 'extension-quibble-not-php74' in templates:
                        continue

                    self.assertIn(
                        '%s-quibble' % kind,
                        templates,
                        'Must have "%s-quibble": %s' % (kind, project['name'])
                    )

            except AssertionError, e:
                errors.append(str(e))

        self.maxDiff = None
        self.assertListEqual([], errors)

    def test_bluespice_repos_use_composer_template(self):
        errors = []
        bsrepos = [r for r in self.getExtSkinRepos()
                   if '/BlueSpice' in r['name']]
        for project in bsrepos:
            if project['name'] in ['mediawiki/extensions/BlueSpiceMenues']:
                # Ignore archived project
                continue
            try:
                if 'template' not in project:
                    continue
                templates = [template['name']
                             for template in project.get('template')]

                # Extract singular 'extension' or 'skin'
                kind = project['name'].split('/')[1][:-1]

                required = [
                    '%s-broken' % kind,
                    '%s-quibble-composer-noselenium' % kind,
                    '%s-quibble-composer' % kind,
                    ]
                self.assertTrue(
                    any([r in templates for r in required]),
                    '%s must have one of [%s]. Got: %s' % (
                        project['name'],
                        ', '.join(required),
                        ', '.join(templates),
                    )
                )
            except AssertionError, e:
                errors.append(str(e))

        self.maxDiff = None
        self.assertListEqual([], errors)

    def test_templates_test_jobs_are_all_in_gate(self):
        errors = []
        self.maxDiff = None

        templates = self.getProjectTemplates()
        for template_name in templates:
            # Some templates are non voting or have no point in adding a job to
            # the gate.
            if 'gate-and-submit' not in templates[template_name]:
                continue

            for pipeline in templates[template_name]:
                if not pipeline.startswith('test'):
                    continue

                # Find the matching gate-and-submit pipeline
                if pipeline == 'test':
                    gate_pipeline = 'gate-and-submit'
                else:
                    suffix = pipeline.rpartition('-')[2]
                    gate_pipeline = 'gate-and-submit' + '-' + suffix

                for test_job in templates[template_name][pipeline]:
                    try:
                        gate_jobs = templates[template_name][gate_pipeline]
                        self.assertIn(
                            test_job,
                            gate_jobs,
                            'Template %s job %s in %s must also be in %s' % (
                                template_name, test_job,
                                pipeline, gate_pipeline)
                        )
                    except AssertionError as e:
                        errors.append(str(e))

        self.assertEqual([], errors)

    def test_pipelines_names_do_not_have_dots(self):
        self.longMessage = True
        for p in self.layout['pipelines']:
            self.assertNotIn('.', p['name'])

    # Wikibase has a lot Selenium tests and we run them in a standalone job
    # (T232759). Any repository depending on Wikibase should follow the same
    # scheme.
    def test_selenium_tests_in_their_own_jobs_when_wikibase(self):
        wikibase_dependents = []
        params = {'ZUUL_BRANCH': 'master'}
        job = FakeJob('quibble-vendor-mysql-php72-docker')

        for repo in sorted(dependencies.keys()):
            if repo.startswith('skins/'):
                full_name = 'mediawiki/' + repo
            else:
                full_name = 'mediawiki/extensions/' + repo
            params['ZUUL_PROJECT'] = full_name

            set_parameters(None, job, params)
            if('\\nmediawiki/extensions/Wikibase\\n'
               not in params['EXT_DEPENDENCIES']):
                continue
            wikibase_dependents.append(full_name)

        self.assertNotEqual(
            [], wikibase_dependents,
            'There must be some repositories depending on Wikibase')

        # No check the layout. The repositories should have Selenium
        # tests split to a different job, which in the Zuul layout means
        # having the templates:
        # - extension-quibble-noselenium
        # - extension-quibble-only-selenium
        split_templates = {
            'extension-quibble-noselenium',
            'extension-quibble-only-selenium'}

        errors = []
        for project in self.layout['projects']:
            if project['name'] not in wikibase_dependents:
                continue
            templates = {t['name'] for t in project.get('template')}
            if templates == ['archived']:
                continue
            try:
                msg = ('%s depends on Wikibase and must have Selenium jobs '
                       'split using %s' % (
                           project['name'],
                           ', '.join(split_templates)
                       ))
                self.assertGreaterEqual(templates, split_templates, msg)
            except AssertionError, e:
                errors.append(str(e))

        self.maxDiff = None
        self.assertListEqual([], errors)
