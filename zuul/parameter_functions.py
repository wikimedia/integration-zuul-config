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

    mw_deps_jobs_starting_with = (
        'mwext-testextension',
        'mwext-qunit',
        'mwext-mw-rspec',
        'mwext-mw-selenium',
        'mw-testskin',
        'mw-testskin-non-voting',
        )
    if job.name.startswith(mw_deps_jobs_starting_with):
        set_mw_dependencies(item, job, params)

    # FIXME rather hacky for selenium jobs (T139740, T137112)
    if job.name.startswith(('mediawiki-core-selenium', 'mwext-mw-selenium')):
        set_mw_dependencies(item, job, params)
        if params['SKIN_DEPENDENCIES']:
            params['SKIN_DEPENDENCIES'] += '\\nmediawiki/skins/Vector'
        else:
            params['SKIN_DEPENDENCIES'] = 'mediawiki/skins/Vector'

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


# This has is used to inject dependencies for MediaWiki jobs.
#
# Values are assumed to be MediaWiki extensions. Skins have to be prefixed with
# 'skins/'.  The has is used by the set_mw_dependencies() parameter function
# below.
dependencies = {
    # Skins are listed first to highlight the skin dependencies
    'skins/BlueSpiceSkin': ['BlueSpiceFoundation'],

    # Extensions
    # One can add a skin by using: 'skin/XXXXX'
    'AbuseFilter': ['AntiSpoof'],
    'ApiFeatureUsage': ['Elastica'],
    'Arrays': ['Loops', 'ParserFunctions', 'Variables'],
    'ArticlePlaceholder': ['Wikibase', 'Scribunto'],
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
    'CustomPage': ['skins/CustomPage'],
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
    'JsonConfig': ['Scribunto'],
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
    'NumberOfComments': ['Comments'],
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
    'Popups': ['BetaFeatures', 'TextExtracts', 'PageImages', 'EventLogging'],
    'PronunciationRecording': ['UploadWizard'],
    'ProofreadPage': ['LabeledSectionTransclusion', 'VisualEditor'],
    'QuickSurveys': ['EventLogging'],
    'Ratings': ['Validator'],
    'RelatedArticles': ['BetaFeatures', 'Cards', 'MobileFrontend'],
    'RevisionSlider': ['BetaFeatures'],
    'Score': ['VisualEditor'],
    'SemanticImageInput': ['SemanticMediaWiki'],
    'SemanticSifter': ['SemanticMediaWiki'],
    'SimpleSurvey': ['PrefSwitch'],
    'SolrStore': ['SemanticMediaWiki'],
    'SpellingDictionary': ['UniversalLanguageSelector'],
    'Spreadsheet': ['PHPExcel'],
    'SubPageList': ['ParserHooks'],
    'SyntaxHighlight_GeSHi': ['VisualEditor'],
    'TitleBlacklist': ['AntiSpoof'],
    'Translate': ['UniversalLanguageSelector', 'EventLogging', 'cldr'],
    'TranslateSvg': ['Translate'],
    'TranslationNotifications': ['Translate'],
    'TwnMainPage': ['Translate'],
    'UniversalLanguageSelector': ['EventLogging'],
    'UploadWizard': ['WikimediaMessages', 'EventLogging', 'AbuseFilter',
                     'SpamBlacklist'],
    'VectorBeta': ['EventLogging'],
    'VikiSemanticTitle': ['VIKI'],
    'VikiTitleIcon': ['VIKI'],
    'VisualEditor': ['Cite'],
    'Wikibase': ['CirrusSearch', 'cldr', 'Elastica', 'GeoData',
                 'Scribunto', 'Capiunto'],
    'WikibaseJavaScriptApi': ['Wikibase'],
    'WikibaseLexeme': ['Wikibase'],
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
    'wikihiero': ['VisualEditor'],
    'ZeroBanner': ['Echo', 'JsonConfig', 'MobileFrontend', 'VisualEditor',
                   'ZeroPortal'],
    'ZeroPortal': ['Echo', 'JsonConfig', 'MobileFrontend', 'Scribunto',
                   'VisualEditor', 'ZeroBanner'],
}


def set_mw_dependencies(item, job, params):
    """
    Inject MediaWiki dependencies based on a built-in hash.

    Reads MediaWiki dependencies for a repository and inject them as
    parameters EXT_DEPENDENCIES or SKIN_DEPENDENCIES. The map is configured via
    the 'dependencies' dictionary above.

    Extensions and skins will both be cloned, the extensions will be listed for
    the extensions autoloader in integration/jenkins.git, skins are
    automatically injected by MediaWiki upon installation.

    :type item: zuul.model.QueueItem
    :type job: zuul.model.Job
    :type params: dict
    """
    if not params['ZUUL_PROJECT'].startswith((
        'mediawiki/extensions/',
        'mediawiki/skins/',
    )):
        return

    split = params['ZUUL_PROJECT'].split('/')

    if len(split) != 3:
        return

    if split[1] == 'skins':
        # Lookup key in 'dependencies'. Example: 'skins/Vector'
        dep_key = 'skins' + '/' + split[-1]
        # 'Vector'
        params['SKIN_NAME'] = split[-1]
    else:
        # Lookup key in 'dependencies. Example: 'Foobar'
        dep_key = split[-1]
        params['EXT_NAME'] = split[-1]

    deps = get_dependencies(dep_key, dependencies)

    # Split extensions and skins
    skin_deps = {d for d in deps if d.startswith('skins/')}
    ext_deps = deps - skin_deps

    # Export with a literal \n character and have bash expand it later via
    # 'echo -e $XXX_DEPENDENCIES'.
    def glue_deps(prefix, deps):
        return '\\n'.join(
            prefix + d for d in sorted(deps)
        )

    params['SKIN_DEPENDENCIES'] = glue_deps('mediawiki/', skin_deps)
    params['EXT_DEPENDENCIES'] = glue_deps('mediawiki/extensions/', ext_deps)


def get_dependencies(key, mapping):
    """
    Get the full set of dependencies required by an extension

    :param key: extension base name or skin as 'skin/BASENAME'
    :param mapping: mapping of repositories to their dependencies
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

    return resolve_deps(key)


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
