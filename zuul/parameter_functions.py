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
    if '-quibble-' in job.name:
        # Quibble takes care of it
        del(params['DISPLAY'])

    php5_jobs = (
        # Qunit localhost uses apache mod_php which is Zend. Lets be consistent
        'mediawiki-core-qunit-selenium-jessie',
        'mwext-qunit-jessie',
        'mwext-qunit-composer-jessie',
        'mediawiki-extensions-qunit-jessie',
        )

    # Sets a $PHP_BIN variable based on the job name
    if 'php55' in job.name:
        params['PHP_BIN'] = 'php5.5'
    elif 'php56' in job.name:
        params['PHP_BIN'] = 'php5'
    elif 'php70' in job.name:
        params['PHP_BIN'] = 'php7.0'
    elif 'hhvm' in job.name:
        params['PHP_BIN'] = 'hhvm'
    elif job.name in php5_jobs:
        params['PHP_BIN'] = 'php5'

    if job.name.endswith('node-6-jessie'):
        # T128091: oojs/ui npm job runs on Jessie which only has HHVM
        params['PHP_BIN'] = 'hhvm'

    mw_deps_jobs_starting_with = (
        'mwext-testextension',
        'mwext-qunit',
        'mwext-ruby-jessie',
        'mwext-mw-selenium',
        'mwskin-mw-selenium',
        'mwskin-testskin',
        'mwext-php70-phan',
        'mwext-phpunit-coverage',
        )
    if job.name.startswith(mw_deps_jobs_starting_with):
        set_mw_dependencies(item, job, params)

    # FIXME rather hacky for selenium jobs (T139740, T137112)
    if job.name.startswith(('mediawiki-core-qunit-selenium',
                            'mwext-ruby-jessie',
                            'mwext-mw-selenium')):
        set_mw_dependencies(item, job, params)
        if 'SKIN_DEPENDENCIES' in params and params['SKIN_DEPENDENCIES']:
            params['SKIN_DEPENDENCIES'] += '\\nmediawiki/skins/Vector'
        else:
            params['SKIN_DEPENDENCIES'] = 'mediawiki/skins/Vector'

    # Enable composer merge plugin in vendor and point it to mediawiki
    # composer.json. That let us easily merge autoload-dev section and thus
    # complete the autoloader in mw-fetch-composer-dev.js
    #
    # T158674
    if (
        'composer' not in job.name
        and params['ZUUL_PROJECT'].startswith('mediawiki/')
    ):
        params['MW_COMPOSER_MERGE_MW_IN_VENDOR'] = 1

    # At least parallel-lint is slow under HHVM
    if params['ZUUL_PROJECT'].startswith('mediawiki/vendor'):
        params['COMPOSER_PROCESS_TIMEOUT'] = 600

    if job.name.startswith('mediawiki-extensions-'):
        set_gated_extensions(item, job, params)

    if job.name.endswith('-jessie'):
        nodepool_params(item, job, params)
    elif job.name.endswith('node-6-jessie'):
        nodepool_params(item, job, params)

    if job.name.endswith('-publish'):
        set_doc_variables(item, job, params)

    # Prevent puppeteer from downloading Chromium, we use the Debian package
    # instead.  T179552 T186748
    if params['ZUUL_PROJECT'].startswith('mediawiki/services/chromium-render'):
        params['PUPPETEER_SKIP_CHROMIUM_DOWNLOAD'] = 'true'

    if 'debian-glue' in job.name:

        # XXX
        # When adding new paramters, make sure the env variable is added as an
        # env_keep in the sudo policy:
        # https://horizon.wikimedia.org/project/sudo/
        #

        if 'backports' in job.name:  # T173999
            params['BACKPORTS'] = 'yes'
        # Always set the value to be safe (T144094)
        params['BUILD_TIMEOUT'] = 30  # minutes
        # Finely tweak jenkins-debian-glue parameters
        if params['ZUUL_PROJECT'] == 'integration/zuul':
            # Uses dh_virtualenv which needs access to pypy.python.org
            params['PBUILDER_USENETWORK'] = 'yes'
            params['DEB_BUILD_OPTIONS'] = 'nocheck'
        elif (params['ZUUL_PROJECT'] == 'operations/debs/varnish4'):
            # VTC tests take forever
            params['BUILD_TIMEOUT'] = 60  # minutes
            params['DEB_BUILD_OPTIONS'] = 'parallel=12'
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
    'skins/MinervaNeue': ['MobileFrontend'],
    'skins/Empty': ['PhpTags'],

    # Extensions
    # One can add a skin by using: 'skin/XXXXX'
    '3D': ['MultimediaViewer'],
    'AbuseFilter': ['AntiSpoof', 'CodeEditor'],
    'AdvancedSearch': ['Translate'],
    'ApiFeatureUsage': ['Elastica'],
    'Arrays': ['Loops', 'ParserFunctions', 'Variables'],
    'ArticlePlaceholder': ['Wikibase', 'Scribunto'],
    'BlogPage': ['Comments', 'SocialProfile', 'VoteNY'],
    'BlueSpiceAbout': ['BlueSpiceFoundation'],
    'BlueSpiceArticleInfo': ['BlueSpiceFoundation'],
    'BlueSpiceAuthors': ['BlueSpiceFoundation'],
    'BlueSpiceAvatars': ['BlueSpiceFoundation'],
    'BlueSpiceBlog': ['BlueSpiceFoundation'],
    'BlueSpiceCategoryManager': ['BlueSpiceFoundation'],
    'BlueSpiceChecklist': ['BlueSpiceFoundation'],
    'BlueSpiceConfigManager': ['BlueSpiceFoundation'],
    'BlueSpiceContextMenu': ['BlueSpiceFoundation'],
    'BlueSpiceCountThings': ['BlueSpiceFoundation'],
    'BlueSpiceDashboards': ['BlueSpiceFoundation'],
    'BlueSpiceEditNotifyConnector': ['BlueSpiceFoundation'],
    'BlueSpiceEmoticons': ['BlueSpiceFoundation'],
    'BlueSpiceExtendedFilelist': ['BlueSpiceFoundation'],
    'BlueSpiceExtendedSearch': ['BlueSpiceFoundation'],
    'BlueSpiceExtendedStatistics': ['BlueSpiceFoundation'],
    'BlueSpiceExtensions': ['BlueSpiceFoundation'],
    'BlueSpiceGroupManager': ['BlueSpiceFoundation'],
    'BlueSpiceHideTitle': ['BlueSpiceFoundation'],
    'BlueSpiceInsertCategory': ['BlueSpiceFoundation'],
    'BlueSpiceInsertFile': ['BlueSpiceFoundation'],
    'BlueSpiceInsertLink': ['BlueSpiceFoundation'],
    'BlueSpiceInsertMagic': ['BlueSpiceFoundation'],
    'BlueSpiceInsertTemplate': ['BlueSpiceFoundation'],
    'BlueSpiceInterWikiLinks': ['BlueSpiceFoundation'],
    'BlueSpiceMenues': ['BlueSpiceFoundation'],
    'BlueSpiceMultiUpload': ['BlueSpiceFoundation'],
    'BlueSpiceNamespaceCSS': ['BlueSpiceFoundation'],
    'BlueSpiceNamespaceManager': ['BlueSpiceFoundation'],
    'BlueSpicePageAccess': ['BlueSpiceFoundation'],
    'BlueSpicePageAssignments': ['BlueSpiceFoundation'],
    'BlueSpicePageTemplates': ['BlueSpiceFoundation'],
    'BlueSpicePageVersion': ['BlueSpiceFoundation'],
    'BlueSpicePagesVisited': ['BlueSpiceFoundation'],
    'BlueSpicePermissionManager': ['BlueSpiceFoundation'],
    'BlueSpiceRSSFeeder': ['BlueSpiceFoundation'],
    'BlueSpiceReaders': ['BlueSpiceFoundation'],
    'BlueSpiceSMWConnector': ['BlueSpiceFoundation'],
    'BlueSpiceSaferEdit': ['BlueSpiceFoundation'],
    'BlueSpiceSignHere': ['BlueSpiceFoundation'],
    'BlueSpiceSmartList': ['BlueSpiceFoundation'],
    'BlueSpiceSubPageTree': ['BlueSpiceFoundation'],
    'BlueSpiceTagCloud': ['BlueSpiceFoundation'],
    'BlueSpiceUEModulePDF': ['BlueSpiceFoundation'],
    'BlueSpiceUniversalExport': ['BlueSpiceFoundation'],
    'BlueSpiceUsageTracker': ['BlueSpiceFoundation'],
    'BlueSpiceUserManager': ['BlueSpiceFoundation'],
    'BlueSpiceUserPreferences': ['BlueSpiceFoundation'],
    'BlueSpiceWatchList': ['BlueSpiceFoundation'],
    'BlueSpiceWhoIsOnline': ['BlueSpiceFoundation'],
    'Capiunto': ['Scribunto'],
    'Challenge': ['SocialProfile'],
    'Cite': ['VisualEditor'],
    'Citoid': ['Cite', 'VisualEditor'],
    'CirrusSearch': ['MwEmbedSupport', 'TimedMediaHandler', 'PdfHandler',
                     'Cite', 'Elastica', 'GeoData', 'BetaFeatures',
                     'SiteMatrix'],
    'CodeEditor': ['WikiEditor'],
    'CodeMirror': ['WikiEditor', 'VisualEditor'],
    'CollaborationKit': ['EventLogging', 'VisualEditor'],
    'ContentTranslation': ['Echo', 'EventLogging', 'GuidedTour',
                           'UniversalLanguageSelector', 'Wikibase',
                           'VisualEditor'],
    'CookieWarning': ['MobileFrontend'],
    'CustomPage': ['skins/CustomPage'],
    'Disambiguator': ['VisualEditor'],
    'DonationInterface': ['ContributionTracking'],
    'EducationProgram': ['cldr', 'WikiEditor'],
    'ElectronPdfService': ['Collection'],
    'FanBoxes': ['SocialProfile'],
    'FileAnnotations': ['EventLogging'],
    'FlaggedRevs': ['Scribunto'],
    'Flow': ['AbuseFilter', 'Echo', 'VisualEditor'],
    'GeoData': ['CirrusSearch'],
    'GettingStarted': ['CentralAuth', 'EventLogging', 'GuidedTour'],
    'Graph': ['CodeEditor', 'JsonConfig', 'VisualEditor'],
    'GraphViz': ['ImageMap'],
    'GuidedTour': ['EventLogging'],
    'GWToolset': ['SyntaxHighlight_GeSHi', 'Scribunto', 'TemplateData'],
    'ImageMetrics': ['EventLogging'],
    'ImageRating': ['VoteNY'],
    'JsonConfig': ['Scribunto'],
    'Kartographer': ['ParserFunctions', 'VisualEditor', 'WikimediaMessages'],
    'LanguageTool': ['VisualEditor'],
    'LifeWeb': ['LifeWebCore', 'Wikibase'],
    'LightweightRDFa': ['WikiEditor'],
    'LoginNotify': ['CentralAuth', 'CheckUser', 'Echo'],
    'MassMessage': ['LiquidThreads'],
    'Math': ['VisualEditor', 'Wikibase'],
    'MathSearch': ['Math'],
    'MobileApp': ['Echo', 'MobileFrontend', 'VisualEditor'],
    'MobileFrontend': ['Echo', 'VisualEditor', 'ZeroBanner', 'MobileApp',
                       'skins/MinervaNeue'],
    'NamespacePopups': ['PagePopups'],
    'NavigationTiming': ['EventLogging'],
    'NSFileRepo': ['Lockdown'],
    'Newsletter': ['Echo'],
    'NewUsersList': ['SocialProfile'],
    'NumberOfComments': ['Comments'],
    'OpenIDConnect': ['PluggableAuth'],
    'OpenStackManager': ['LdapAuthentication'],
    'PageTriage': ['WikiLove'],
    'PageViewInfo': ['Graph'],
    'ParserFunctions': ['Scribunto'],
    'PhpTagsFunctions': ['PhpTags'],
    'PhpTagsSPARQL': ['PhpTags'],
    'PhpTagsSMW': ['PhpTags'],
    'PhpTagsStorage': ['PhpTags', 'PhpTagsFunctions', 'PhpTagsWiki',
                       'PhpTagsWidgets'],
    'PhpTagsWidgets': ['PhpTags', 'PhpTagsFunctions', 'PhpTagsWiki'],
    'PhpTagsWiki': ['PhpTags', 'PhpTagsFunctions'],
    'PictureGame': ['SocialProfile'],
    'PollNY': ['SocialProfile'],
    'Popups': ['BetaFeatures', 'TextExtracts', 'PageImages', 'EventLogging'],
    'Premoderation': ['skins/Vector'],
    'PronunciationRecording': ['UploadWizard'],
    'ProofreadPage': ['LabeledSectionTransclusion', 'VisualEditor'],
    'PropertySuggester': ['Wikibase'],
    'QuickSurveys': ['EventLogging'],
    'QuizGame': ['SocialProfile'],
    'RandomFeaturedUser': ['SocialProfile'],
    'RandomGameUnit': ['SocialProfile', 'PictureGame', 'PollNY', 'QuizGame'],
    'RandomUsersWithAvatars': ['SocialProfile'],
    'RegexFun': ['ParserFunctions', 'Arrays'],
    'RelatedArticles': ['BetaFeatures', 'MobileFrontend'],
    'RevisionSlider': ['MobileFrontend'],
    'Score': ['VisualEditor'],
    'SemanticLinks': ['VisualEditor'],
    'SiteMetrics': ['SocialProfile'],
    'SiteScout': ['Comments', 'SocialProfile', 'VoteNY'],
    'SimpleSAMLphp': ['PluggableAuth'],
    'SimpleSurvey': ['PrefSwitch'],
    'SpamBlacklist': ['CheckUser', 'EventLogging'],
    'SpamDiffTool': ['SpamBlacklist'],
    'SpellingDictionary': ['UniversalLanguageSelector'],
    'SportsTeams': ['SocialProfile', 'UserStatus'],
    'SyntaxHighlight_GeSHi': ['VisualEditor'],
    'TemplateWizard': ['TemplateData', 'WikiEditor'],
    'TimedMediaHandler': ['MwEmbedSupport'],
    'TitleBlacklist': ['AntiSpoof', 'Scribunto'],
    'TheWikipediaLibrary': ['Echo'],
    'Thanks': ['Echo'],
    'Translate': ['UniversalLanguageSelector', 'EventLogging', 'cldr'],
    'TranslateSvg': ['Translate'],
    'TranslationNotifications': ['Translate'],
    'TwnMainPage': ['Translate'],
    'TwoColConflict': ['BetaFeatures', 'EventLogging', 'WikiEditor'],
    'UniversalLanguageSelector': ['EventLogging'],
    'UploadWizard': ['WikimediaMessages', 'EventLogging', 'AbuseFilter',
                     'SpamBlacklist'],
    'UserStatus': ['SocialProfile', 'SportsTeams'],
    'VikiSemanticTitle': ['VIKI'],
    'VikiTitleIcon': ['VIKI'],
    'VisualEditor': ['Cite'],
    'Wikibase': [
        'CirrusSearch',
        'cldr',
        'Elastica',
        'GeoData',
        'Scribunto',
        'Capiunto',
        'Echo',
        'PropertySuggester',
        'WikibaseQuality',
        'WikibaseQualityConstraints',
        'WikimediaBadges'
    ],
    'WikibaseJavaScriptApi': ['Wikibase'],
    'WikibaseLexeme': ['Wikibase'],
    'WikibaseMediaInfo': ['Wikibase'],
    'WikibaseQuality': ['Wikibase'],
    'WikibaseQualityConstraints': ['Wikibase', 'WikibaseQuality'],
    'WikibaseQualityExternalValidation': ['Wikibase', 'WikibaseQuality'],
    'Wikidata.org': ['Wikibase'],
    'WikidataPageBanner': ['Wikibase'],
    'WikiEditor': ['EventLogging'],
    'WikimediaBadges': ['Wikibase'],
    'WikimediaEvents': ['EventLogging'],
    'Wikisource': ['Wikibase'],
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
    'CheckUser',
    'CirrusSearch',
    'Cite',
    'cldr',
    'CodeEditor',
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
    'NavigationTiming',
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
    # Note: pre-1.31 this is switched out for Wikidata build extension
    'Wikibase',
    'WikiEditor',
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
    # Prior to 1.31, we need to use the "Wikidata" build extension
    use_wikidata = ('REL1_27', 'REL1_29', 'REL1_30')
    if params['ZUUL_BRANCH'] in use_wikidata:
        deps.remove('Wikibase')
        deps.append('Wikidata')
    deps = sorted(list(set(deps)))

    params['EXT_DEPENDENCIES'] = '\\n'.join(
        'mediawiki/extensions/' + dep for dep in deps
    )

    # So we can cd $EXT_NAME && composer test - T161895
    split = params['ZUUL_PROJECT'].split('/')
    if len(split) == 3 and split[1] == 'extensions':
        params['EXT_NAME'] = split[-1]


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
