"""
Parameter functions for zuul jobs

Combined into one Python function due to T125498
"""

import re


def set_parameters(item, job, params):
    """
    :type item: zuul.model.QueueItem
    :type job: zuul.model.Job
    :type params: dict
    """

    # Sets a $PHP_BIN variable based on the job name
    if 'php55' in job.name:
        params['PHP_BIN'] = 'php5'
    elif 'hhvm' in job.name:
        params['PHP_BIN'] = 'hhvm'
    elif job.name == 'mediawiki-core-phpcs':
        # T126394: This should always be HHVM
        params['PHP_BIN'] = 'hhvm'

    ext_deps_jobs = ('mwext-testextension', 'mwext-qunit', 'mwext-mw-selenium')
	skin_deps_jobs = ('mwext-testextension', 'mwext-qunit')
    if job.name.startswith(ext_deps_jobs):
        set_ext_dependencies(item, job, params)

    if job.name.startswith(skin_deps_jobs):
        set_skin_dependencies(item, job, params)

    if job.name in ['tox-jessie', 'rake-jessie',
                    'integration-jjb-config-diff']:
        offline_when_complete(item, job, params)
    elif re.search('^tox-.*-jessie$', job.name):
        offline_when_complete(item, job, params)

    if job.name.endswith('-publish'):
        set_doc_variables(item, job, params)

dependencies = {
    'AbuseFilter': ['AntiSpoof'],
    'ApiFeatureUsage': ['Elastica'],
    'ArticlePlaceholder': ['Wikibase', 'Scribunto'],
    'Capiunto': ['Scribunto'],
    'Cite': ['VisualEditor'],
    'Citoid': ['Cite', 'VisualEditor'],
    'CirrusSearch': ['MwEmbedSupport', 'TimedMediaHandler', 'PdfHandler',
                     'Cite'],
    'CodeEditor': ['WikiEditor'],
    'ContentTranslation': ['Echo', 'EventLogging', 'GuidedTour',
                           'UniversalLanguageSelector', 'Wikidata'],
    'Disambiguator': ['VisualEditor'],
    'EducationProgram': ['cldr'],
    'FlaggedRevs': ['Scribunto'],
    'Flow': ['AbuseFilter', 'CheckUser', 'ConfirmEdit', 'SpamBlacklist',
             'Echo', 'EventLogging', 'VisualEditor'],
    'Gather': ['PageImages', 'TextExtracts', 'MobileFrontend', 'Echo',
               'VisualEditor'],
    'GettingStarted': ['CentralAuth', 'EventLogging', 'GuidedTour'],
    'GoogleLogin': ['GoogleAPIClient'],
    'Graph': ['CodeEditor', 'JsonConfig', 'VisualEditor'],
    'GuidedTour': ['EventLogging'],
    'GWToolset': ['SyntaxHighlight_GeSHi', 'Scribunto', 'TemplateData'],
    'ImageMetrics': ['EventLogging'],
    'Kartographer': ['VisualEditor'],
    'LanguageTool': ['VisualEditor'],
    'LifeWeb': ['LifeWebCore'],
    'MassMessage': ['LiquidThreads'],
    'Math': ['VisualEditor', 'Wikidata'],
    'MathSearch': ['Math'],
    'MobileFrontend': ['Echo', 'VisualEditor'],
    'NavigationTiming': ['EventLogging'],
    'OpenStackManager': ['LdapAuthentication'],
    'PronunciationRecording': ['UploadWizard'],
    'ProofreadPage': ['LabeledSectionTransclusion'],
    'QuickSurveys': ['EventLogging'],
    'RelatedArticles': ['BetaFeatures', 'Cards', 'MobileFrontend'],
    'Score': ['VisualEditor'],
    'SemanticFormsInputs': ['SemanticForms'],
    'SyntaxHighlight_GeSHi': ['VisualEditor'],
    'Thanks': ['Echo', 'Flow', 'MobileFrontend'],
    'VectorBeta': ['EventLogging'],
    'VikiSemanticTitle': ['VIKI'],
    'VikiTitleIcon': ['VIKI'],
    'VisualEditor': ['Cite'],
    'Wikibase': ['CirrusSearch', 'cldr', 'Elastica', 'GeoData',
                 'Scribunto', 'Capiunto'],
    'WikibaseQuality': ['Wikibase'],
    'WikibaseQualityConstraints': ['Wikibase', 'WikibaseQuality'],
    'WikibaseQualityExternalValidation': ['Wikibase', 'WikibaseQuality'],
    'Wikidata': ['cldr', 'Elastica', 'GeoData', 'Scribunto'],
    'WikidataPageBanner': ['Wikidata'],
    'WikimediaBadges': ['Wikibase'],
    'WikimediaPageViewInfo': ['Graph'],
}

skin_dependencies = {
}

def set_ext_dependencies(item, job, params):
    """
    Reads dependencies from the yaml file and adds them as a parameter
    :type item: zuul.model.QueueItem
    :type job: zuul.model.Job
    :type params: dict
    """
    if not params['ZUUL_PROJECT'].startswith('mediawiki/extensions/'):
        return
    # mediawiki/extensions/FooBar
    split = params['ZUUL_PROJECT'].split('/')
    if len(split) != 3:
        # mediawiki/extensions/FooBar/blah
        # mediawiki/extensions
        return

    # FooBar
    ext_name = split[-1]
    params['EXT_NAME'] = ext_name

    deps = get_dependencies(ext_name, dependencies)

    # Export with a literal \n character and have bash expand it later
    params['EXT_DEPENDENCIES'] = '\\n'.join(
        'mediawiki/extensions/' + dep for dep in sorted(deps)
    )

def set_skin_dependencies(item, job, params):
    """
    Reads dependencies from the yaml file and adds them as a parameter
    :type item: zuul.model.QueueItem
    :type job: zuul.model.Job
    :type params: dict
    """
    if not params['ZUUL_PROJECT_SKIN'].startswith('mediawiki/skins/'):
        return
    # mediawiki/skins/FooBar
    split = params['ZUUL_PROJECT_SKIN'].split('/')
    if len(split) != 3:
        # mediawiki/skins/FooBar/blah
        # mediawiki/skins
        return

    # FooBar
    skin_name = split[-1]
    params['SKIN_NAME'] = skin_name

    deps = get_dependencies(skin_name, skin_dependencies)

    # Export with a literal \n character and have bash expand it later
    params['SKIN_DEPENDENCIES'] = '\\n'.join(
        'mediawiki/skins/' + dep for dep in sorted(deps)
    )

def get_dependencies(ext_name, mapping):
    """
    Get the full set of dependencies required by an extension
    :param ext_name: extension name
    :param mapping: mapping of extensions to their dependencies
    :return: set of dependencies, recursively processed
    """
    resolved = set()

    def resolve_deps(ext):
        resolved.add(ext)
        deps = set()

        if ext in mapping:
            for dep in mapping[ext]:
                deps.add(dep)

                if dep not in resolved:
                    deps = deps.union(resolve_deps(dep))

        return deps

    return resolve_deps(ext_name)


# Instruct Jenkins Gearman plugin to put a node offline on job completion.
# Ie for nodepool
def offline_when_complete(item, job, params):
    params['OFFLINE_NODE_WHEN_COMPLETE'] = '1'


def set_doc_variables(item, job, params):
    change = item.change
    doc_subpath = ''

    # ref-updated
    # Tags: 'refs/tags/foo'
    # Branch: 'master'
    if hasattr(change, 'ref'):
        tag = re.match(r'^refs/tags/(.*)', change.ref)
        if tag:
            doc_subpath = tag.group(1)
        else:
            doc_subpath = change.ref
    # Changes
    elif hasattr(change, 'refspec'):
        doc_subpath = change.branch

    if doc_subpath:
        params['DOC_SUBPATH'] = doc_subpath

    # Normalize the project name by removing /'s
    if 'ZUUL_PROJECT' in params:
        params['DOC_PROJECT'] = params['ZUUL_PROJECT'].replace('/', '-')
