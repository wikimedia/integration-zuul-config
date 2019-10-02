# Parse Zuul layout.yaml file
#
# Copyright (c) 2016 - Antoine "hashar" Musso
# Copyright (c) 2016 - Wikimedia Foundation Inc.

import os
import unittest

import yaml


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
            'extension-quibble-php72-plus',
            'skin-tests',
            'skin-quibble',
            'extension-gate',
            'quibble-vendor',
            )
        errors = []
        for project in self.getExtSkinRepos():

            # Special case!
            if project['name'] == 'mediawiki/extensions/DonationInterface':
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
