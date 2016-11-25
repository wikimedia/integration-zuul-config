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
        'mw-testskin',
        'mw-testskin-non-voting',
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
    if 'php53' in job.name:
        params['PHP_BIN'] = 'php5'
    if 'php55' in job.name:
        params['PHP_BIN'] = 'php5'
    elif 'php70' in job.name:
        params['PHP_BIN'] = 'php7.0'
    elif 'hhvm' in job.name:
        params['PHP_BIN'] = 'hhvm'
    elif job.name in hhvm_jobs:
        # T126394: This should always be HHVM
        params['PHP_BIN'] = 'hhvm'
    elif job.name in php5_jobs:
        params['PHP_BIN'] = 'php5'

    if job.name.endswith('node-4'):
        # T128091: oojs/ui npm job runs on Jessie which only has HHVM
        params['PHP_BIN'] = 'hhvm'

    ext_deps_jobs_starting_with = (
        'mwext-testextension',
        'mwext-qunit',
        'mwext-mw-selenium',
        )
    if job.name.startswith(ext_deps_jobs_starting_with):
        set_ext_dependencies(item, job, params)

    if job.name.startswith('mediawiki-extensions-'):
        set_gated_extensions(item, job, params)

    if job.name.endswith('-jessie'):
        nodepool_params(item, job, params)
    if job.name.endswith('-trusty'):
        nodepool_params(item, job, params)
    elif job.name.endswith('node-4'):
        nodepool_params(item, job, params)
    elif job.name.endswith('node-0.10'):
        nodepool_params(item, job, params)
    elif job.name in ['integration-jjb-config-diff',
                      'mwext-VisualEditor-publish']:
        nodepool_params(item, job, params)

    if job.name.endswith('-publish'):
        set_doc_variables(item, job, params)

    # Needs BUNDLE_PATH
    if job.name.endswith('yard-publish'):
        nodepool_params(item, job, params)

    if 'debian-glue' in job.name:
        # Always set the value to be safe (T144094)
        params['BUILD_TIMEOUT'] = 30  # minutes
        # Finely tweak jenkins-debian-glue parameters
        if params['ZUUL_PROJECT'] == 'integration/zuul':
            # Uses dh_virtualenv which needs access to pypy.python.org
            params['PBUILDER_USENETWORK'] = 'yes'
            params['DEB_BUILD_OPTIONS'] = 'nocheck'
        elif (params['ZUUL_PROJECT'] ==
                'operations/debs/contenttranslation/giella-sme'):
            # Heavy build T143546
            params['BUILD_TIMEOUT'] = 180  # minutes

dependencies = {
    'extensions/AbuseFilter': ['extensions/AntiSpoof'],
    'extensions/ApiFeatureUsage': ['extensions/Elastica'],
    'extensions/Arrays': ['extensions/Loops', 'extensions/ParserFunctions', 'extensions/Variables'],
    'ArticlePlaceholder': ['extensions/Wikibase', 'extensions/Scribunto'],
    'BlueSpiceExtensions': ['BlueSpiceFoundation'],
    'Capiunto': ['Scribunto'],
    'Cite': ['VisualEditor'],
    'Citoid': ['Cite', 'VisualEditor'],
    'CirrusSearch': ['MwEmbedSupport', 'TimedMediaHandler', 'PdfHandler',
                     'Cite'],
    'CodeEditor': ['WikiEditor'],
    'CollaborationKit': ['EventLogging', 'VisualEditor'],
    'ContentTranslation': ['Echo', 'EventLogging', 'GuidedTour',
                           'UniversalLanguageSelector', 'Wikidata'],
    'CookieWarning': ['MobileFrontend'],
    'Disambiguator': ['VisualEditor'],
    'DonationInterface': ['ContributionTracking'],
    'EducationProgram': ['cldr', 'WikiEditor'],
    'ElectronPdfService': ['Collection'],
    'FileAnnotations': ['EventLogging'],
    'FlaggedRevs': ['Scribunto'],
    'GettingStarted': ['CentralAuth', 'EventLogging', 'GuidedTour'],
    'Graph': ['CodeEditor', 'JsonConfig', 'VisualEditor'],
    'GuidedTour': ['EventLogging'],
    'GWToolset': ['SyntaxHighlight_GeSHi', 'Scribunto', 'TemplateData'],
    'ImageMetrics': ['EventLogging'],
    'Kartographer': ['ParserFunctions', 'VisualEditor', 'WikimediaMessages'],
    'LanguageTool': ['VisualEditor'],
    'LifeWeb': ['LifeWebCore', 'Wikibase'],
    'LightweightRDFa': ['WikiEditor'],
    'Maps': ['Validator'],
    'MassMessage': ['LiquidThreads'],
    'Math': ['VisualEditor', 'Wikidata'],
    'MathSearch': ['Math'],
    'MobileApp': ['Echo', 'MobileFrontend', 'VisualEditor'],
    'MobileFrontend': ['Echo', 'VisualEditor', 'ZeroBanner', 'MobileApp'],
    'NavigationTiming': ['EventLogging'],
    'NSFileRepo': ['Lockdown'],
    'OpenIDConnect': ['PluggableAuth'],
    'OpenStackManager': ['LdapAuthentication'],
    'ORES': ['BetaFeatures'],
    'PageTriage': ['WikiLove'],
    'PageViewInfo': ['Graph'],
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
    'RevisionSlider': ['BetaFeatures'],
    'Score': ['VisualEditor'],
    'SemanticFormsInputs': ['SemanticForms'],
    'SemanticImageInput': ['SemanticMediaWiki'],
    'SemanticSifter': ['SemanticMediaWiki'],
    'SimpleSurvey': ['PrefSwitch'],
    'SolrStore': ['SemanticMediaWiki'],
    'Spreadsheet': ['PHPExcel'],
    'SubPageList': ['ParserHooks'],
    'SyntaxHighlight_GeSHi': ['VisualEditor'],
    'TitleBlacklist': ['AntiSpoof'],
    'Translate': ['UniversalLanguageSelector', 'EventLogging', 'cldr'],
    'TranslateSvg': ['Translate'],
    'TranslationNotifications': ['Translate'],
    'TwnMainPage': ['Translate'],
    'UniversalLanguageSelector': ['EventLogging'],
    'UploadWizard': ['WikimediaMessages', 'EventLogging'],
    'VectorBeta': ['EventLogging'],
    'VikiSemanticTitle': ['VIKI'],
    'VikiTitleIcon': ['VIKI'],
    'VisualEditor': ['Cite'],
    'Wikibase': ['CirrusSearch', 'cldr', 'Elastica', 'GeoData',
                 'Scribunto', 'Capiunto'],
    'extensions/WikibaseJavaScriptApi': ['extensions/Wikibase'],
    'extensions/WikibaseLexeme': ['extensions/Wikibase'],
    'extensions/WikibaseMediaInfo': ['Wikibase'],
    'extensions/WikibaseQuality': ['Wikibase'],
    'extensions/WikibaseQualityConstraints': ['Wikibase', 'WikibaseQuality'],
    'extensions/WikibaseQualityExternalValidation': ['Wikibase', 'WikibaseQuality'],
    'extensions/Wikidata': ['cldr', 'Elastica',
                 'GeoData', 'Scribunto'],
    'extensions/Wikidata.org': ['Wikibase'],
    'extensions/WikidataPageBanner': ['Wikidata'],
    'extensions/WikimediaBadges': ['Wikibase'],
    'extensions/WikimediaEvents': ['EventLogging'],
    'extensions/wikihiero': ['VisualEditor'],
    'extensions/ZeroBanner': ['Echo', 'JsonConfig', 'MobileFrontend', 'VisualEditor',
                   'ZeroPortal'],
    'extensions/ZeroPortal': ['extensions/Echo', 'JsonConfig', 'MobileFrontend', 'Scribunto',
                   'VisualEditor', 'ZeroBanner'],
}


def set_ext_dependencies(item, job, params):
    """
    Reads dependencies from the yaml file and adds them as a parameter
    :type item: zuul.model.QueueItem
    :type job: zuul.model.Job
    :type params: dict
    """
    if not params['ZUUL_PROJECT'].startswith('mediawiki/'):
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
        'mediawiki/' + dep for dep in sorted(deps)
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


gatedextensions = [
    'AbuseFilter',
    'Babel',
    'Cards',
    'CheckUser',
    'CirrusSearch',
    'Cite',
    'cldr',
    'ConfirmEdit',
    'Echo',
    'Elastica',
    'EventLogging',
    'Flow',
    'GeoData',
    'GlobalCssJs',
    'GuidedTour',
    'JsonConfig',
    'MobileApp',
    'MobileFrontend',
    'MwEmbedSupport',
    'ParserFunctions',
    'PdfHandler',
    'SandboxLink',
    'SpamBlacklist',
    'SiteMatrix',
    'Thanks',
    'TimedMediaHandler',
    'Translate',
    'UniversalLanguageSelector',
    'VisualEditor',
    'Wikidata',
    'ZeroBanner',
    'ZeroPortal',
]


def set_gated_extensions(item, job, params):
    deps = []
    # When triggered from the experimental pipeline, add the project to the
    # list of dependencies. Used to inject an extension which is not yet
    # participating.
    if(
        params['ZUUL_PIPELINE'] == 'experimental' and
        params['ZUUL_PROJECT'].startswith('mediawiki/extensions/')
    ):
        deps.append(params['ZUUL_PROJECT'].split('/')[-1])

    deps.extend(gatedextensions)
    deps = sorted(list(set(deps)))

    params['EXT_DEPENDENCIES'] = '\\n'.join(
        'mediawiki/extensions/' + dep for dep in deps
    )


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
