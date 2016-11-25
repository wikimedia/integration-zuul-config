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
    'extensions/Arrays': ['extensions/Loops', 'extensions/ParserFunctions',
                          'extensions/Variables'],
    'extensions/ArticlePlaceholder': ['extensions/Wikibase',
                                      'extensions/Scribunto'],
    'extensions/BlueSpiceExtensions': ['extensions/BlueSpiceFoundation'],
    'extensions/Capiunto': ['extensions/Scribunto'],
    'extensions/Cite': ['extensions/VisualEditor'],
    'extensions/Citoid': ['extensions/Cite', 'extensions/VisualEditor'],
    'extensions/CirrusSearch': ['extensions/MwEmbedSupport',
                                'extensions/TimedMediaHandler',
                                'extensions/PdfHandler', 'Cite'],
    'extensions/CodeEditor': ['extensions/WikiEditor'],
    'extensions/CollaborationKit': ['extensions/EventLogging',
                                    'extensions/VisualEditor'],
    'extensions/ContentTranslation': ['extensions/Echo',
                                      'extensions/EventLogging',
                                      'extensions/GuidedTour',
                                      'extensions/UniversalLanguageSelector',
                                      'extensions/Wikidata'],
    'extensions/CookieWarning': ['extensions/MobileFrontend'],
    'extensions/Disambiguator': ['extensions/VisualEditor'],
    'extensions/DonationInterface': ['extensions/ContributionTracking'],
    'extensions/EducationProgram': ['extensions/cldr',
                                    'extensions/WikiEditor'],
    'extensions/ElectronPdfService': ['Collection'],
    'extensions/FileAnnotations': ['EventLogging'],
    'extensions/FlaggedRevs': ['extensions/Scribunto'],
    'extensions/GettingStarted': ['extensions/CentralAuth',
                                  'extensions/EventLogging',
                                  'extensions/GuidedTour'],
    'extensions/Graph': ['extensions/CodeEditor', 'extensions/JsonConfig',
                         'extensions/VisualEditor'],
    'extensions/GuidedTour': ['extensions/EventLogging'],
    'extensions/GWToolset': ['extensions/SyntaxHighlight_GeSHi',
                             'extensions/Scribunto',
                             'extensions/TemplateData'],
    'extensions/ImageMetrics': ['extensions/EventLogging'],
    'extensions/Kartographer': ['extensions/ParserFunctions',
                                'extensions/VisualEditor',
                                'extensions/WikimediaMessages'],
    'extensions/LanguageTool': ['extensions/VisualEditor'],
    'extensions/LifeWeb': ['extensions/LifeWebCore', 'extensions/Wikibase'],
    'extensions/LightweightRDFa': ['extensions/WikiEditor'],
    'extensions/Maps': ['extensions/Validator'],
    'extensions/MassMessage': ['extensions/LiquidThreads'],
    'extensions/Math': ['extensions/VisualEditor', 'extensions/Wikidata'],
    'extensions/MathSearch': ['extensions/Math'],
    'extensions/MobileApp': ['extensions/Echo', 'extensions/MobileFrontend',
                             'extensions/VisualEditor'],
    'extensions/MobileFrontend': ['extensions/Echo', 'extensions/VisualEditor',
                                  'extensions/ZeroBanner',
                                  'extensions/MobileApp'],
    'extensions/NavigationTiming': ['extensions/EventLogging'],
    'extensions/NSFileRepo': ['extensions/Lockdown'],
    'extensions/OpenIDConnect': ['extensions/PluggableAuth'],
    'extensions/OpenStackManager': ['extensions/LdapAuthentication'],
    'extensions/ORES': ['extensions/BetaFeatures'],
    'extensions/PageTriage': ['extensions/WikiLove'],
    'extensions/PageViewInfo': ['extensions/Graph'],
    'extensions/PhpTagsFunctions': ['extensions/PhpTags'],
    'extensions/PhpTagsStorage': ['extensions/PhpTags',
                                  'extensions/PhpTagsFunctions',
                                  'extensions/PhpTagsWiki',
                                  'extensions/PhpTagsWidgets'],
    'extensions/PhpTagsWidgets': ['extensions/PhpTags',
                                  'extensions/PhpTagsFunctions',
                                  'extensions/PhpTagsWiki'],
    'extensions/PhpTagsWiki': ['extensions/PhpTags',
                               'extensions/PhpTagsFunctions'],
    'extensions/PictureGame': ['extensions/SocialProfile'],
    'extensions/PollNY': ['extensions/SocialProfile'],
    'extensions/Popups': ['extensions/BetaFeatures', 'extensions/TextExtracts',
                          'extensions/PageImages'],
    'extensions/PronunciationRecording': ['extensions/UploadWizard'],
    'extensions/ProofreadPage': ['extensions/LabeledSectionTransclusion',
                                 'extensions/VisualEditor'],
    'extensions/QuickSurveys': ['extensions/EventLogging'],
    'extensions/Ratings': ['extensions/Validator'],
    'extensions/RelatedArticles': ['extensions/BetaFeatures',
                                   'extensions/Cards',
                                   'extensions/MobileFrontend'],
    'extensions/RevisionSlider': ['extensions/BetaFeatures'],
    'extensions/Score': ['extensions/VisualEditor'],
    'extensions/SemanticFormsInputs': ['extensions/SemanticForms'],
    'extensions/SemanticImageInput': ['extensions/SemanticMediaWiki'],
    'extensions/SemanticSifter': ['extensions/SemanticMediaWiki'],
    'extensions/SimpleSurvey': ['extensions/PrefSwitch'],
    'extensions/SolrStore': ['extensions/SemanticMediaWiki'],
    'extensions/Spreadsheet': ['extensions/PHPExcel'],
    'extensions/SubPageList': ['extensions/ParserHooks'],
    'extensions/SyntaxHighlight_GeSHi': ['extensions/VisualEditor'],
    'extensions/TitleBlacklist': ['extensions/AntiSpoof'],
    'extensions/Translate': ['extensions/UniversalLanguageSelector',
                             'extensions/EventLogging',
                             'extensions/cldr'],
    'extensions/TranslateSvg': ['extensions/Translate'],
    'extensions/TranslationNotifications': ['extensions/Translate'],
    'extensions/TwnMainPage': ['extensions/Translate'],
    'extensions/UniversalLanguageSelector': ['extensions/EventLogging'],
    'extensions/UploadWizard': ['extensions/WikimediaMessages',
                                'extensions/EventLogging'],
    'extensions/VectorBeta': ['extensions/EventLogging'],
    'extensions/VikiSemanticTitle': ['extensions/VIKI'],
    'extensions/VikiTitleIcon': ['extensions/VIKI'],
    'extensions/VisualEditor': ['extensions/Cite'],
    'extensions/Wikibase': ['extensions/CirrusSearch',
                            'extensions/cldr',
                            'extensions/Elastica',
                            'extensions/GeoData',
                            'extensions/Scribunto',
                            'extensions/Capiunto'],
    'extensions/WikibaseJavaScriptApi': ['extensions/Wikibase'],
    'extensions/WikibaseLexeme': ['extensions/Wikibase'],
    'extensions/WikibaseMediaInfo': ['extensions/Wikibase'],
    'extensions/WikibaseQuality': ['extensions/Wikibase'],
    'extensions/WikibaseQualityConstraints': ['extensions/Wikibase',
                                              'extensions/WikibaseQuality'],
    'extensions/WikibaseQualityExternalValidation': ['extensions/Wikibase',
                                                 'extensions/WikibaseQuality'],
    'extensions/Wikidata': ['extensions/cldr', 'extensions/Elastica',
                            'extensions/GeoData', 'extensions/Scribunto'],
    'extensions/Wikidata.org': ['extensions/Wikibase'],
    'extensions/WikidataPageBanner': ['extensions/Wikidata'],
    'extensions/WikimediaBadges': ['extensions/Wikibase'],
    'extensions/WikimediaEvents': ['extensions/EventLogging'],
    'extensions/wikihiero': ['extensions/VisualEditor'],
    'extensions/ZeroBanner': ['extensions/Echo', 'extensions/JsonConfig',
                              'extensions/MobileFrontend',
                              'extensions/VisualEditor',
                              'extensions/ZeroPortal'],
    'extensions/ZeroPortal': ['extensions/Echo', 'extensions/JsonConfig',
                              'extensions/MobileFrontend',
                              'extensions/Scribunto',
                              'extensions/VisualEditor',
                              'extensions/ZeroBanner'],
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
