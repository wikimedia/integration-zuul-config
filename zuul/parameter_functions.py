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

    # Xvfb display provided via puppet
    params['DISPLAY'] = ':94'

    hhvm_jobs = (
        'mediawiki-core-phpcs-trusty',
        'mw-tools-codesniffer-mwcore-testrun',
        )
    php5_jobs = (
        # Qunit localhost uses apache mod_php which is Zend. Lets be consistent
        'mediawiki-core-qunit-jessie',
        'mwext-qunit-jessie',
        'mwext-qunit-composer-jessie',
        'mediawiki-extensions-qunit-jessie',
        )

    # Sets a $PHP_BIN variable based on the job name
    if 'php55' in job.name:
        params['PHP_BIN'] = 'php5'
    elif 'hhvm' in job.name:
        params['PHP_BIN'] = 'hhvm'
    elif job.name in hhvm_jobs:
        # T126394: This should always be HHVM
        params['PHP_BIN'] = 'hhvm'
    elif job.name in php5_jobs:
        params['PHP_BIN'] = 'php5'

    if job.name.endswith('node-4.3'):
        # T128091: oojs/ui npm job runs on Jessie which only has HHVM
        params['PHP_BIN'] = 'hhvm'
    elif job.name.endswith('node-0.10'):
        params['PHP_BIN'] = 'php5'

    ext_deps_jobs_starting_with = (
        'mwext-testextension',
        'mwext-qunit',
        'mwext-mw-selenium',
        )
    if job.name.startswith(ext_deps_jobs_starting_with):
        set_ext_dependencies(item, job, params)

    if job.name.endswith('-jessie'):
        nodepool_params(item, job, params)
    if job.name.endswith('-trusty'):
        nodepool_params(item, job, params)
    elif job.name.endswith('node-4.3'):
        nodepool_params(item, job, params)
    elif job.name.endswith('node-0.10'):
        nodepool_params(item, job, params)
    elif job.name in ['integration-jjb-config-diff']:
        nodepool_params(item, job, params)

    if job.name.endswith('-publish'):
        set_doc_variables(item, job, params)

dependencies = {
    'AbuseFilter': ['AntiSpoof'],
    'ApiFeatureUsage': ['Elastica'],
    'Arrays': ['Loops', 'ParserFunctions', 'Variables'],
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
    'DonationInterface': ['ContributionTracking'],
    'EducationProgram': ['cldr'],
    'FlaggedRevs': ['Scribunto'],
    'GettingStarted': ['CentralAuth', 'EventLogging', 'GuidedTour'],
    'Graph': ['CodeEditor', 'JsonConfig', 'VisualEditor'],
    'GuidedTour': ['EventLogging'],
    'GWToolset': ['SyntaxHighlight_GeSHi', 'Scribunto', 'TemplateData'],
    'ImageMetrics': ['EventLogging'],
    'Kartographer': ['VisualEditor'],
    'LanguageTool': ['VisualEditor'],
    'LifeWeb': ['LifeWebCore'],
    'LightweightRDFa': ['WikiEditor'],
    'Maps': ['Validator'],
    'MassMessage': ['LiquidThreads'],
    'Math': ['VisualEditor', 'Wikidata'],
    'MathSearch': ['Math'],
    'MobileApp': ['Echo', 'MobileFrontend', 'VisualEditor'],
    'MobileFrontend': ['Echo', 'VisualEditor'],
    'NavigationTiming': ['EventLogging'],
    'NSFileRepo': ['Lockdown'],
    'OpenIDConnect': ['PluggableAuth'],
    'OpenStackManager': ['LdapAuthentication'],
    'PhpTagsFunctions': ['PhpTags'],
    'PhpTagsStorage': ['PhpTags', 'PhpTagsFunctions', 'PhpTagsWiki',
                       'PhpTagsWidgets'],
    'PhpTagsWidgets': ['PhpTags', 'PhpTagsFunctions', 'PhpTagsWiki'],
    'PhpTagsWiki': ['PhpTags', 'PhpTagsFunctions'],
    'PictureGame': ['SocialProfile'],
    'PollNY': ['SocialProfile'],
    'Popups': ['BetaFeatures', 'TextExtracts', 'PageImages'],
    'PronunciationRecording': ['UploadWizard'],
    'ProofreadPage': ['LabeledSectionTransclusion', 'VisualEditor'],
    'QuickSurveys': ['EventLogging'],
    'Ratings': ['Validator'],
    'RelatedArticles': ['BetaFeatures', 'Cards', 'MobileFrontend'],
    'Score': ['VisualEditor'],
    'SemanticFormsInputs': ['SemanticForms'],
    'SemanticSifter': ['SemanticMediaWiki'],
    'SimpleSurvey': ['PrefSwitch'],
    'SolrStore': ['SemanticMediaWiki'],
    'Spreadsheet': ['PHPExcel'],
    'SyntaxHighlight_GeSHi': ['VisualEditor'],
    'TitleBlacklist': ['AntiSpoof'],
    'Translate': ['UniversalLanguageSelector', 'EventLogging', 'cldr'],
    'TranslateSvg': ['Translate'],
    'TranslationNotifications': ['Translate'],
    'TwnMainPage': ['Translate'],
    'UniversalLanguageSelector': ['EventLogging'],
    'VectorBeta': ['EventLogging'],
    'VikiSemanticTitle': ['VIKI'],
    'VikiTitleIcon': ['VIKI'],
    'VisualEditor': ['Cite'],
    'Wikibase': ['CirrusSearch', 'cldr', 'Elastica', 'GeoData',
                 'Scribunto', 'Capiunto'],
    'WikibaseMediaInfo': ['Wikibase'],
    'WikibaseQuality': ['Wikibase'],
    'WikibaseQualityConstraints': ['Wikibase', 'WikibaseQuality'],
    'WikibaseQualityExternalValidation': ['Wikibase', 'WikibaseQuality'],
    'Wikidata': ['cldr', 'Elastica',
                 'GeoData', 'Scribunto'],
    'Wikidata.org': ['Wikibase'],
    'WikidataPageBanner': ['Wikidata'],
    'WikimediaBadges': ['Wikibase'],
    'WikimediaEvents': ['EventLogging'],
    'WikimediaPageViewInfo': ['Graph'],
    'wikihiero': ['VisualEditor'],
    'ZeroBanner': ['Echo', 'JsonConfig', 'MobileFrontend', 'VisualEditor'],
    'ZeroPortal': ['Echo', 'JsonConfig', 'MobileFrontend', 'Scribunto',
                   'VisualEditor', 'ZeroBanner'],
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


def nodepool_params(item, job, params):
    # Instruct Jenkins Gearman plugin to put a node offline on job completion.
    params['OFFLINE_NODE_WHEN_COMPLETE'] = '1'

    # Bundle defaults to install to GEM_HOME which on Debian is the system
    # directory. It thus attempt to sudo which is not available to the
    # 'jenkins' user on Nodepool instances.
    #
    # To avoid injecting material in the source workspace, install material
    # in the parent directory.
    #
    # If changing this: DO UPDATE castor-save as well!!!
    params['BUNDLE_PATH'] = '/home/jenkins/workspace/vendor/bundle'


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
        params['DOC_BASENAME'] = params['ZUUL_PROJECT'].split('/')[-1]
