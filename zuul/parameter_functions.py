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
    if 'quibble' in job.name:
        # Quibble takes care of it
        del(params['DISPLAY'])

    # Sets a $PHP_BIN variable based on the job name
    if 'php70' in job.name:
        params['PHP_BIN'] = 'php7.0'

    mw_deps_jobs_starting_with = (
        'mwselenium-quibble',
        'mwext-php72-phan',
        'mwskin-php72-phan',
        'mwext-phpunit-coverage',
        'mwext-codehealth',
        'mediawiki-quibble',
        'quibble',
        )
    if job.name.startswith(mw_deps_jobs_starting_with):
        set_mw_dependencies(item, job, params)

    # Special jobs for Wikibase - T188717
    if job.name == 'wikibase-client-docker':
        params['EXT_DEPENDENCIES'] = '\\n'.join([
            'mediawiki/extensions/Scribunto',
            'mediawiki/extensions/Capiunto',
            'mediawiki/extensions/cldr',
            'mediawiki/extensions/Echo',
        ])

    if job.name == 'wikibase-repo-docker':
        params['EXT_DEPENDENCIES'] = '\\n'.join([
            'mediawiki/extensions/CirrusSearch',
            'mediawiki/extensions/Elastica',
            'mediawiki/extensions/GeoData',
            'mediawiki/extensions/cldr',
        ])

    if job.name == 'parsoidsvc-parsertests-docker':
        params['EXT_DEPENDENCIES'] = '\\n'.join([
            'mediawiki/extensions/Cite',
            'mediawiki/extensions/Poem',
            'mediawiki/extensions/TimedMediaHandler',
        ])

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

    # parallel-lint can be slow
    if params['ZUUL_PROJECT'].startswith('mediawiki/vendor'):
        params['COMPOSER_PROCESS_TIMEOUT'] = 600

    if job.name.startswith('wmf-quibble-'):
        set_gated_extensions(item, job, params)

    if job.name.endswith('-publish') or 'codehealth' in job.name:
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

        if 'nocheck' in job.name:
            params['DEB_BUILD_OPTIONS'] = 'nocheck'
        if 'backports' in job.name:  # T173999
            params['BACKPORTS'] = 'yes'
        # Always set the value to be safe (T144094)
        params['BUILD_TIMEOUT'] = 30  # minutes
        # Finely tweak jenkins-debian-glue parameters
        if params['ZUUL_PROJECT'] == 'integration/zuul':
            # Uses dh_virtualenv which needs access to pypy.python.org
            params['PBUILDER_USENETWORK'] = 'yes'
        elif (params['ZUUL_PROJECT'] == 'operations/debs/varnish4'):
            # VTC tests take forever
            params['BUILD_TIMEOUT'] = 60  # minutes
            params['DEB_BUILD_OPTIONS'] = 'parallel=12'
        elif (params['ZUUL_PROJECT']
              == 'operations/software/varnish/varnishkafka'):
            # needed for librdkafka1 >= 0.11.5
            params['BACKPORTS'] = 'yes'
        elif (params['ZUUL_PROJECT'] == 'operations/software/atskafka'):
            # needed by go build to access gopkg.in
            params['PBUILDER_USENETWORK'] = 'yes'
        elif (params['ZUUL_PROJECT'] == 'operations/debs/hue'):
            # fetches from pypi/npm
            params['PBUILDER_USENETWORK'] = 'yes'
        elif (params['ZUUL_PROJECT'] == 'operations/debs/trafficserver'):
            # Building ATS takes a while
            params['BUILD_TIMEOUT'] = 60  # minutes
            # Backports needed on stretch for libbrotli-dev and a recent
            # debhelper version (>= 11)
            params['BACKPORTS'] = 'yes'
        elif (params['ZUUL_PROJECT']
              == 'operations/debs/contenttranslation/giella-sme'):
            # Heavy build T143546
            params['BUILD_TIMEOUT'] = 180  # minutes


# This hash is used to inject dependencies for MediaWiki jobs.
#
# Values are assumed to be MediaWiki extensions. Skins have to be prefixed with
# 'skins/'.  The has is used by the set_mw_dependencies() parameter function
# below.
# Note! This list is not used by Phan. Scroll down farther for that list.
dependencies = {
    # Skins are listed first to highlight the skin dependencies
    'skins/BlueSpiceSkin': ['BlueSpiceFoundation'],
    'skins/BlueSpiceCalumma': ['BlueSpiceFoundation'],
    'skins/MinervaNeue': ['MobileFrontend'],
    'skins/Empty': ['PhpTags'],
    'skins/Refreshed': ['SocialProfile'],

    # Extensions
    # One can add a skin by using: 'skin/XXXXX'
    '3D': ['MultimediaViewer'],
    'AbuseFilter': ['AntiSpoof', 'CentralAuth', 'CodeEditor',
                    'CheckUser', 'Echo', 'Renameuser', 'Thanks'],
    'AdvancedSearch': ['Translate'],
    'ApiFeatureUsage': ['Elastica'],
    'Arrays': ['Loops', 'ParserFunctions', 'Variables'],
    'ArticlePlaceholder': ['Wikibase', 'Scribunto'],
    'BlogPage': ['Comments', 'SocialProfile', 'VoteNY'],
    'BlueSpiceAbout': ['BlueSpiceFoundation'],
    'BlueSpiceArticleInfo': ['BlueSpiceFoundation'],
    'BlueSpiceArticlePreviewCapture': ['BlueSpiceFoundation'],
    'BlueSpiceAuthors': ['BlueSpiceFoundation'],
    'BlueSpiceAvatars': ['BlueSpiceFoundation'],
    'BlueSpiceBookshelf': ['BlueSpiceFoundation'],
    'BlueSpiceBookshelfUI': ['BlueSpiceFoundation', 'BlueSpiceBookshelf'],
    'BlueSpiceCategoryCheck': ['BlueSpiceFoundation'],
    'BlueSpiceCategoryManager': ['BlueSpiceFoundation'],
    'BlueSpiceChecklist': ['BlueSpiceFoundation', 'VisualEditor'],
    'BlueSpiceConfigManager': ['BlueSpiceFoundation'],
    'BlueSpiceContextMenu': ['BlueSpiceFoundation'],
    'BlueSpiceCountThings': ['BlueSpiceFoundation', 'VisualEditor'],
    'BlueSpiceCustomMenu': ['BlueSpiceFoundation'],
    'BlueSpiceDashboards': ['BlueSpiceFoundation'],
    'BlueSpiceDistributionConnector': ['BlueSpiceFoundation'],
    'BlueSpiceEchoConnector': ['BlueSpiceFoundation', 'Echo'],
    'BlueSpiceEditNotifyConnector': [
        'BlueSpiceFoundation',
        'BlueSpiceEchoConnector',
        'EditNotify',
    ],
    'BlueSpiceEmoticons': ['BlueSpiceFoundation'],
    'BlueSpiceExpiry': ['BlueSpiceFoundation', 'BlueSpiceReminder'],
    'BlueSpiceExportTables': ['BlueSpiceFoundation',
                              'BlueSpiceUEModuleTable2Excel'],
    'BlueSpiceExtendedFilelist': ['BlueSpiceFoundation'],
    'BlueSpiceExtendedSearch': ['BlueSpiceFoundation', 'VisualEditor'],
    'BlueSpiceExtendedStatistics': ['BlueSpiceFoundation',
                                    'BlueSpiceExtendedSearch'],
    'BlueSpiceExtensions': ['BlueSpiceFoundation'],
    'BlueSpiceFilterableTables': ['BlueSpiceFoundation'],
    'BlueSpiceGroupManager': ['BlueSpiceFoundation'],
    'BlueSpiceHideTitle': ['BlueSpiceFoundation'],
    'BlueSpiceInsertCategory': ['BlueSpiceFoundation'],
    'BlueSpiceInsertFile': ['BlueSpiceFoundation'],
    'BlueSpiceInsertLink': [
        'BlueSpiceFoundation',
        'BlueSpiceVisualEditorConnector',
    ],
    'BlueSpiceInsertMagic': ['BlueSpiceFoundation', 'VisualEditor'],
    'BlueSpiceFoundation': ['ExtJSBase'],
    'BlueSpiceInsertTemplate': ['BlueSpiceFoundation'],
    'BlueSpiceInterWikiLinks': ['BlueSpiceFoundation'],
    'BlueSpiceMultiUpload': ['BlueSpiceFoundation'],
    'BlueSpiceNamespaceCSS': ['BlueSpiceFoundation'],
    'BlueSpiceNamespaceManager': ['BlueSpiceFoundation'],
    'BlueSpiceNSFileRepoConnector': ['BlueSpiceFoundation', 'NSFileRepo'],
    'BlueSpicePageAccess': ['BlueSpiceFoundation'],
    'BlueSpicePageAssignments': ['BlueSpiceFoundation'],
    'BlueSpicePageFormsConnector': ['BlueSpiceFoundation', 'PageForms'],
    'BlueSpicePageTemplates': ['BlueSpiceFoundation'],
    'BlueSpicePageVersion': ['BlueSpiceFoundation'],
    'BlueSpicePagesVisited': [
        'BlueSpiceFoundation',
        'BlueSpiceWhoIsOnline',
    ],
    'BlueSpicePermissionManager': ['BlueSpiceFoundation'],
    'BlueSpicePrivacy': ['BlueSpiceFoundation'],
    'BlueSpiceQrCode': ['BlueSpiceFoundation'],
    'BlueSpiceRating': ['BlueSpiceFoundation'],
    'BlueSpiceRSSFeeder': ['BlueSpiceFoundation'],
    'BlueSpiceReaders': ['BlueSpiceFoundation'],
    'BlueSpiceReadConfirmation': ['BlueSpiceFoundation'],
    'BlueSpiceReminder': ['BlueSpiceFoundation'],
    'BlueSpiceSMWConnector': ['BlueSpiceFoundation'],
    'BlueSpiceSocial': ['BlueSpiceFoundation', 'BlueSpiceExtendedSearch'],
    'BlueSpiceSocialArticleActions': ['BlueSpiceFoundation', 'BlueSpiceSocial',
                                      'BlueSpiceExtendedSearch'],
    'BlueSpiceSocialBlog': ['BlueSpiceFoundation', 'BlueSpiceSocial',
                            'BlueSpiceExtendedSearch'],
    'BlueSpiceSocialComments': ['BlueSpiceFoundation', 'BlueSpiceSocial',
                                'BlueSpiceExtendedSearch'],
    'BlueSpiceSocialMicroBlog': ['BlueSpiceFoundation', 'BlueSpiceSocial',
                                 'BlueSpiceExtendedSearch'],
    'BlueSpiceSocialProfile': ['BlueSpiceFoundation', 'BlueSpiceSocial',
                               'BlueSpiceExtendedSearch', 'BlueSpiceAvatars'],
    'BlueSpiceSocialRating': ['BlueSpiceFoundation', 'BlueSpiceSocial',
                              'BlueSpiceExtendedSearch', 'BlueSpiceRating'],
    'BlueSpiceSocialResolve': ['BlueSpiceFoundation', 'BlueSpiceSocial',
                               'BlueSpiceExtendedSearch'],
    'BlueSpiceSocialTags': ['BlueSpiceFoundation', 'BlueSpiceSocial',
                            'BlueSpiceExtendedSearch'],
    'BlueSpiceSocialTimelineUpdate': ['BlueSpiceFoundation', 'BlueSpiceSocial',
                                      'BlueSpiceExtendedSearch'],
    'BlueSpiceSocialTopics': ['BlueSpiceFoundation', 'BlueSpiceSocial',
                              'BlueSpiceExtendedSearch'],
    'BlueSpiceSocialWatch': ['BlueSpiceFoundation', 'BlueSpiceSocial',
                             'BlueSpiceExtendedSearch'],
    'BlueSpiceSocialWikiPage': ['BlueSpiceFoundation', 'BlueSpiceSocial',
                                'BlueSpiceExtendedSearch',
                                'BlueSpiceMultiUpload'],
    'BlueSpiceSaferEdit': ['BlueSpiceFoundation'],
    'BlueSpiceSignHere': ['BlueSpiceFoundation'],
    'BlueSpiceSmartList': ['BlueSpiceFoundation', 'VisualEditor'],
    'BlueSpiceSubPageTree': ['BlueSpiceFoundation'],
    'BlueSpiceTagCloud': ['BlueSpiceFoundation'],
    'BlueSpiceUEModuleBookPDF': ['BlueSpiceFoundation',
                                 'BlueSpiceUniversalExport',
                                 'BlueSpiceBookshelf',
                                 'BlueSpiceUEModulePDF'],
    'BlueSpiceUEModuleDOCX': [
        'BlueSpiceFoundation',
        'BlueSpiceUniversalExport',
    ],
    'BlueSpiceUEModulePDF': [
        'BlueSpiceFoundation',
        'BlueSpiceUniversalExport',
    ],
    'BlueSpiceUEModulePDFRecursive': [
        'BlueSpiceFoundation',
        'BlueSpiceUniversalExport',
    ],
    'BlueSpiceUEModulePDFSubpages': [
        'BlueSpiceFoundation',
        'BlueSpiceUniversalExport',
    ],
    'BlueSpiceUEModuleHTML': [
        'BlueSpiceFoundation',
        'BlueSpiceUniversalExport',
    ],
    'BlueSpiceUEModuleTable2Excel': ['BlueSpiceFoundation',
                                     'BlueSpiceUniversalExport'],
    'BlueSpiceUniversalExport': ['BlueSpiceFoundation'],
    'BlueSpiceUsageTracker': ['BlueSpiceFoundation'],
    'BlueSpiceUserInfo': ['BlueSpiceFoundation'],
    'BlueSpiceUserManager': ['BlueSpiceFoundation'],
    'BlueSpiceUserSidebar': ['BlueSpiceFoundation'],
    'BlueSpiceVisualDiff': ['BlueSpiceFoundation'],
    'BlueSpiceVisualEditorConnector': [
        'BlueSpiceFoundation',
        'OOJSPlus',
        'VisualEditor',
    ],
    'BlueSpiceWatchList': ['BlueSpiceFoundation'],
    'BlueSpiceWhoIsOnline': ['BlueSpiceFoundation'],
    'BlueSpiceWikiExplorer': ['BlueSpiceFoundation'],
    'BounceHandler': ['Echo', 'CentralAuth'],
    'Campaigns': ['EventLogging'],
    'Capiunto': ['Scribunto'],
    'CentralNotice': ['EventLogging'],
    'Challenge': ['SocialProfile'],
    'CheckUser': ['CentralAuth', 'GuidedTour', 'Renameuser'],
    'Cite': ['ParserFunctions', 'VisualEditor'],
    'Citoid': ['Cite', 'VisualEditor'],
    'CirrusSearch': ['TimedMediaHandler', 'PdfHandler', 'Cite', 'Elastica',
                     'GeoData', 'BetaFeatures', 'SiteMatrix',
                     'WikibaseCirrusSearch'],
    'CodeEditor': ['WikiEditor'],
    'CodeMirror': ['WikiEditor', 'VisualEditor'],
    'CognitiveProcessDesigner': ['PageForms', 'BlueSpiceFoundation',
                                 'BlueSpiceUEModulePDF'],
    'CollaborationKit': ['EventLogging', 'VisualEditor'],
    'ConfigManager': ['BlueSpiceFoundation'],
    'ContentTranslation': ['AbuseFilter', 'Echo', 'EventLogging',
                           'UniversalLanguageSelector', 'VisualEditor'],
    'ContributorsAddon': ['Contributors'],
    'CookieWarning': ['MobileFrontend'],
    'CreateAPage': ['WikiEditor'],
    'CustomPage': ['skins/CustomPage'],
    'Dashiki': ['JsonConfig'],
    'DiscussionTools': ['VisualEditor', 'Linter'],
    'Disambiguator': ['VisualEditor'],
    'Echo': ['CentralAuth', 'EventLogging'],
    'ElectronPdfService': ['Collection'],
    'EmailAuthorization': ['PluggableAuth'],
    'EventBus': ['EventStreamConfig'],
    'EventLogging': ['EventStreamConfig'],
    'ExternalGuidance': ['MobileFrontend', 'UniversalLanguageSelector'],
    'FanBoxes': ['SocialProfile'],
    'FlexiSkin': ['BlueSpiceFoundation', 'OOJSPlus', 'CodeEditor'],
    'FileAnnotations': ['EventLogging'],
    'FileExporter': ['BetaFeatures'],
    'FileImporter': ['CentralAuth', 'WikiEditor'],
    'FlaggedRevs': ['Scribunto'],
    'Flow': ['AbuseFilter', 'Echo', 'VisualEditor'],
    'FundraiserLandingPage': ['EventLogging'],
    'FundraisingTranslateWorkflow': ['Translate'],
    'GeoData': ['CirrusSearch'],
    'GettingStarted': ['CentralAuth', 'EventLogging', 'GuidedTour'],
    'GlobalCheckUser': ['CentralAuth', 'CheckUser'],
    'GlobalContribs': ['Editcount'],
    'Graph': ['CodeEditor', 'JsonConfig', 'VisualEditor'],
    'GraphViz': ['ImageMap'],
    'GrowthExperiments': ['skins/MinervaNeue', 'PageViewInfo', 'PageImages',
                          'EventLogging', 'Flow', 'MobileFrontend', 'Echo'],
    'GuidedTour': ['EventLogging'],
    'GWToolset': ['SyntaxHighlight_GeSHi', 'Scribunto', 'TemplateData'],
    'HierarchyBuilder': ['PageForms'],
    'ImageMetrics': ['EventLogging'],
    'ImageRating': ['VoteNY'],
    'Jade': ['AbuseFilter', 'SpamBlacklist'],
    'JsonConfig': ['Scribunto', 'Kartographer'],
    'Kartographer': ['JsonConfig', 'ParserFunctions', 'VisualEditor',
                     'WikimediaMessages'],
    'LanguageTool': ['VisualEditor'],
    'LDAPAuthentication2': ['LDAPProvider', 'PluggableAuth'],
    'LDAPAuthorization': ['LDAPProvider', 'PluggableAuth'],
    'LDAPGroups': ['LDAPProvider'],
    'LDAPUserInfo': ['LDAPProvider'],
    'LifeWeb': ['LifeWebCore', 'Wikibase'],
    'LightweightRDFa': ['WikiEditor'],
    'LoginNotify': ['CentralAuth', 'CheckUser', 'Echo'],
    'MachineVision': ['Wikibase', 'WikibaseMediaInfo', 'Echo'],
    'MassMessage': ['Flow', 'LiquidThreads'],
    'Math': ['VisualEditor', 'Wikibase'],
    'MathSearch': ['Math'],
    'MobileApp': ['Echo', 'MobileFrontend', 'VisualEditor', 'AbuseFilter'],
    'MobileFrontend': ['Echo', 'VisualEditor', 'MobileApp',
                       'skins/MinervaNeue'],
    'MultimediaViewer': ['BetaFeatures'],
    'NamespacePopups': ['PagePopups'],
    'NavigationTiming': ['EventLogging'],
    'NSFileRepo': ['Lockdown'],
    'Newsletter': ['Echo'],
    'OAuth': ['Echo'],
    'OAuthRateLimiter': ['OAuth'],
    'OpenIDConnect': ['PluggableAuth'],
    'OpenStackManager': ['LdapAuthentication', 'Echo', 'TitleBlacklist'],
    'PageTriage': ['WikiLove', 'ORES', 'Echo'],
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
    'Popups': ['BetaFeatures', 'TextExtracts', 'PageImages', 'EventLogging',
               'Cite'],
    'Premoderation': ['skins/Vector'],
    'PronunciationRecording': ['UploadWizard'],
    'ProofreadPage': ['LabeledSectionTransclusion', 'VisualEditor'],
    'PropertySuggester': ['Wikibase'],
    'PushNotifications': ['Echo'],
    'QuickSurveys': ['EventLogging'],
    'QuizGame': ['Renameuser', 'SocialProfile'],
    'RandomGameUnit': ['SocialProfile', 'PictureGame', 'PollNY', 'QuizGame'],
    'RegexFun': ['ParserFunctions', 'Arrays'],
    'RelatedArticles': ['BetaFeatures', 'MobileFrontend'],
    'ReplaceText': ['AdminLinks'],
    'RevisionSlider': ['MobileFrontend'],
    'Score': ['VisualEditor', 'TimedMediaHandler', 'Wikibase'],
    'Scribunto': ['SyntaxHighlight_GeSHi'],
    'SemanticLinks': ['VisualEditor'],
    'Shibboleth': ['PluggableAuth'],
    'SiteMetrics': ['SocialProfile'],
    'SiteScout': ['Comments', 'SocialProfile', 'VoteNY'],
    'SimpleSAMLphp': ['PluggableAuth'],
    'SimpleSurvey': ['PrefSwitch'],
    'SoftRedirector': ['VisualEditor'],
    'SpamBlacklist': ['AbuseFilter', 'CheckUser', 'EventLogging'],
    'SpamDiffTool': ['SpamBlacklist'],
    'SpellingDictionary': ['UniversalLanguageSelector'],
    'SportsTeams': ['SocialProfile', 'UserStatus'],
    'StopForumSpam': ['AbuseFilter'],
    'SyntaxHighlight_GeSHi': ['VisualEditor'],
    'TEI': ['CodeMirror', 'Math', 'VisualEditor'],
    'TemplateWizard': ['TemplateData', 'WikiEditor'],
    'TitleBlacklist': ['AntiSpoof', 'Scribunto'],
    'TheWikipediaLibrary': ['Echo', 'CentralAuth', 'GlobalPreferences'],
    'Thanks': ['Echo', 'Flow', 'MobileFrontend'],
    'Translate': ['UniversalLanguageSelector', 'EventLogging', 'cldr'],
    'TranslateSvg': ['Translate'],
    'TranslationNotifications': ['MassMessage', 'Translate'],
    'TopTenPages': ['HitCounters'],
    'TorBlock': ['AbuseFilter'],
    'TwitterCards': ['TextExtracts'],
    'TwnMainPage': ['Translate'],
    'TwoColConflict': ['BetaFeatures', 'EventLogging', 'WikiEditor'],
    'UniversalLanguageSelector': ['EventLogging'],
    'UploadWizard': ['WikimediaMessages', 'EventLogging', 'AbuseFilter',
                     'SpamBlacklist'],
    'UserStatus': ['SocialProfile', 'SportsTeams'],
    'VEForAll': ['VisualEditor'],
    'VikiSemanticTitle': ['VIKI'],
    'VikiTitleIcon': ['VIKI'],
    'VisualEditor': ['Cite', 'TemplateData', 'FlaggedRevs', 'ConfirmEdit'],
    'WebAuthn': ['OATHAuth'],
    'WebDAVClientIntegration': ['WebDAV'],
    'WebDAVMinorSave': ['WebDAV'],
    'WhoIsWatching': ['Echo'],
    'Wikibase': [
        'ArticlePlaceholder',
        'CirrusSearch',
        'cldr',
        'Elastica',
        'GeoData',
        # temporarily dropped due to excessive slowness (T231198)
        # 'Scribunto',
        # 'Capiunto',
        'Echo',
        'PropertySuggester',
        'WikibaseQualityConstraints',
        'WikimediaBadges',
        'WikibaseMediaInfo',
        'WikibaseLexeme',
        'skins/MinervaNeue',
        'MobileFrontend',
    ],
    'WikibaseCirrusSearch': ['Wikibase', 'CirrusSearch'],
    'WikibaseLexeme': ['Wikibase'],
    'WikibaseLexemeCirrusSearch': ['Wikibase', 'WikibaseLexeme',
                                   'CirrusSearch',
                                   'WikibaseCirrusSearch'],
    'WikibaseManifest': ['Wikibase'],
    'WikibaseMediaInfo': ['Wikibase', 'UniversalLanguageSelector',
                          'WikibaseCirrusSearch'],
    'WikibaseQualityConstraints': ['Wikibase'],
    'Wikidata.org': ['Wikibase'],
    'WikidataPageBanner': ['Wikibase'],
    'WikiEditor': ['EventLogging', 'WikimediaEvents'],
    'WikimediaBadges': ['Wikibase'],
    'WikimediaEvents': ['EventLogging'],
    'Wikisource': ['Wikibase'],
    'wikihiero': ['VisualEditor'],
}

# Dependencies used in phan jobs.
# This list is *not* recursively processed.
phan_dependencies = {
    'skins/MinervaNeue': ['Echo', 'MobileFrontend'],
    'skins/Refreshed': ['SocialProfile'],
    'AbuseFilter': ['CheckUser', 'CentralAuth', 'Renameuser'],
    'AdvancedSearch': ['BetaFeatures'],
    'ApiFeatureUsage': ['Elastica'],
    'ArticlePlaceholder': ['Scribunto', 'Wikibase'],
    'BounceHandler': ['CentralAuth', 'Echo'],
    'Campaigns': ['EventLogging', 'MobileFrontend'],
    'Capiunto': ['Scribunto'],
    'CentralAuth': ['AbuseFilter', 'AntiSpoof', 'EventLogging', 'MassMessage',
                    'MobileFrontend', 'Renameuser', 'TitleBlacklist',
                    'UserMerge', 'Echo'],
    'CentralNotice': ['CentralAuth', 'MobileFrontend', 'Translate', 'cldr'],
    'CheckUser': ['CentralAuth', 'EventLogging', 'GuidedTour', 'Renameuser'],
    'CirrusSearch': ['BetaFeatures', 'Elastica', 'SiteMatrix'],
    'Citoid': ['Cite', 'VisualEditor'],
    'CleanChanges': ['cldr'],
    'CognitiveProcessDesigner': ['PageForms', 'BlueSpiceFoundation',
                                 'BlueSpiceUEModulePDF'],
    'CollaborationKit': ['EventLogging', 'PageImages', 'VisualEditor', 'Flow'],
    'ConfirmEdit': ['Math'],
    'ContactPage': ['ConfirmEdit'],
    'ContentTranslation': ['AbuseFilter', 'BetaFeatures', 'CentralAuth',
                           'Echo', 'EventLogging', 'GlobalPreferences'],
    'Dashiki': ['JsonConfig'],
    'Disambiguator': ['VisualEditor'],
    'DiscussionTools': ['VisualEditor', 'Linter'],
    'Echo': ['CentralAuth', 'EventLogging'],
    'EventBus': ['CentralNotice', 'EventStreamConfig'],
    'FileExporter': ['BetaFeatures'],
    'FlaggedRevs': ['Scribunto', 'Echo', 'GoogleNewsSitemap', 'MobileFrontend',
                    'skins/Vector'],
    'Flow': ['AbuseFilter', 'BetaFeatures', 'CentralAuth', 'CirrusSearch',
             'ConfirmEdit', 'Echo', 'Elastica', 'GuidedTour', 'LiquidThreads',
             'SpamBlacklist', 'VisualEditor'],
    'FundraisingTranslateWorkflow': ['Translate'],
    'GettingStarted': ['CentralAuth', 'CirrusSearch', 'MobileFrontend',
                       'VisualEditor'],
    'GeoData': ['CirrusSearch', 'Elastica'],
    'GrowthExperiments': ['EventLogging', 'PageImages', 'PageViewInfo',
                          'skins/MinervaNeue', 'Flow', 'MobileFrontend',
                          'Echo'],
    'ImageRating': ['SocialProfile', 'VoteNY'],
    'intersection': ['PageImages'],
    'JsonConfig': ['Scribunto', 'Kartographer'],
    'Kartographer': ['GeoData', 'JsonConfig'],
    'LiquidThreads': ['Renameuser'],
    'LoginNotify': ['CentralAuth', 'Echo'],
    'MachineVision': ['Wikibase', 'WikibaseMediaInfo', 'Echo'],
    'Math': ['VisualEditor', 'Wikibase'],
    'MobileApp': ['AbuseFilter'],
    'MobileFrontend': ['AbuseFilter', 'CentralAuth', 'LiquidThreads',
                       'PageImages', 'Wikibase', 'XAnalytics'],
    'Newsletter': ['Echo'],
    'OAuth': ['Echo'],
    'OAuthRateLimiter': ['OAuth'],
    'OpenStackManager': ['LdapAuthentication', 'Echo', 'TitleBlacklist'],
    'PageForms': ['AdminLinks', 'Cargo', 'PageSchemas'],
    'PageTriage': ['Echo', 'ORES'],
    'ParserFunctions': ['Scribunto'],
    'Petition': ['CheckUser', 'cldr'],
    'Popups': ['BetaFeatures', 'EventLogging', 'Gadgets'],
    'PropertySuggester': ['Wikibase'],
    'QuizGame': ['Renameuser', 'SocialProfile'],
    'ReadingLists': ['SiteMatrix'],
    'RelatedArticles': ['Disambiguator'],
    'ReplaceText': ['AdminLinks'],
    'Score': ['TimedMediaHandler', 'Wikibase'],
    'Scribunto': ['SyntaxHighlight_GeSHi'],
    'SecurePoll': ['CentralAuth'],
    'SocialProfile': ['Echo'],
    'SoftRedirector': ['VisualEditor'],
    'SpamBlacklist': ['CheckUser', 'EventLogging'],
    'StopForumSpam': ['AbuseFilter'],
    'TEI': ['Math'],
    'Thanks': ['CheckUser', 'Echo', 'Flow', 'MobileFrontend'],
    'TheWikipediaLibrary': ['Echo', 'CentralAuth', 'GlobalPreferences'],
    'TimedMediaHandler': ['BetaFeatures'],
    'TitleBlacklist': ['AntiSpoof', 'Scribunto'],
    'TorBlock': ['AbuseFilter'],
    'Translate': ['AbuseFilter', 'AdminLinks', 'cldr', 'Elastica',
                  'TranslationNotifications'],
    'TranslationNotifications': ['CentralAuth', 'MassMessage', 'SiteMatrix',
                                 'Translate'],
    'TwoColConflict': ['BetaFeatures', 'EventLogging', 'WikiEditor'],
    'UniversalLanguageSelector': ['Babel', 'BetaFeatures', 'MobileFrontend',
                                  'cldr'],
    'UploadWizard': ['EventLogging'],
    'WebAuthn': ['OATHAuth'],
    'WikiEditor': ['EventLogging', 'WikimediaEvents'],
    'WikiLove': ['Flow', 'LiquidThreads'],
    'WikibaseCirrusSearch': ['CirrusSearch', 'Wikibase'],
    'WikibaseLexeme': ['Wikibase'],
    'WikibaseLexemeCirrusSearch': ['CirrusSearch', 'Wikibase',
                                   'WikibaseCirrusSearch', 'WikibaseLexeme'],
    'WikibaseManifest': ['Wikibase'],
    'WikibaseMediaInfo': ['Wikibase', 'CirrusSearch', 'Elastica',
                          'WikibaseCirrusSearch'],
    'WikibaseQualityConstraints': ['Wikibase'],
    'Wikidata.org': ['Wikibase'],
    'WikidataPageBanner': ['PageImages', 'Wikibase'],
    'WikimediaBadges': ['Wikibase'],
    'WikimediaEvents': ['AbuseFilter', 'BetaFeatures', 'CentralAuth',
                        'EventLogging', 'GrowthExperiments', 'MobileFrontend'],
    'WikimediaIncubator': ['CentralAuth'],
    'WikimediaMaintenance': ['CentralAuth', 'CirrusSearch', 'cldr', 'Cognate',
                             'MassMessage', 'Wikibase'],
    'WikimediaMessages': ['GuidedTour', 'ORES', 'skins/MinervaNeue'],
    'Wikisource': ['Wikibase']
}


def set_mw_dependencies(item, job, params):
    """
    Inject MediaWiki dependencies based on a built-in hash.

    Reads MediaWiki dependencies for a repository and inject them as
    parameters EXT_DEPENDENCIES or SKIN_DEPENDENCIES. The map is configured via
    the 'dependencies' dictionary above.

    Extensions and skins will be cloned by Zuul-cloner.

    :type item: zuul.model.QueueItem
    :type job: zuul.model.Job
    :type params: dict
    """
    if not params['ZUUL_PROJECT'].startswith((
        'mediawiki/extensions/',
        'mediawiki/skins/',
        'mediawiki/services/parsoid',
    )):
        return

    split = params['ZUUL_PROJECT'].split('/')

    if len(split) != 3:
        return

    # extensions/Foo, skins/Bar
    params['THING_SUBNAME'] = '/'.join(split[1:3])

    if split[1] == 'skins':
        # Lookup key in 'dependencies'. Example: 'skins/Vector'
        dep_key = 'skins' + '/' + split[-1]
        # 'Vector'
        params['SKIN_NAME'] = split[-1]
    elif split[1] == 'services':
        # Lookup key in 'dependencies. Example: 'services/parsoid'
        dep_key = 'services' + '/' + split[-1]
        params['SERVICE_NAME'] = split[-1]
    else:
        # Lookup key in 'dependencies. Example: 'Foobar'
        dep_key = split[-1]
        params['EXT_NAME'] = split[-1]

    if '-phan-' in job.name:
        mapping = phan_dependencies
        recurse = False
    else:
        mapping = dependencies
        recurse = True

    deps = get_dependencies(dep_key, mapping, recurse)

    # Split extensions and skins
    skin_deps = {d for d in deps if d.startswith('skins/')}
    ext_deps = deps - skin_deps

    # EventStreamConfig only requires MW >= REL1_35.
    # Therefore remove it from REL1_31 and REL1_34. T249514
    if (
        params['ZUUL_BRANCH'] in ['REL1_31', 'REL1_34']
        and 'EventStreamConfig' in ext_deps
    ):
        ext_deps.remove('EventStreamConfig')

    # WikibaseCirrusSearch doesn't exist in MW == REL1_31.
    # Therefore remove it from REL1_31. T258715
    if (
        params['ZUUL_BRANCH'] == 'REL1_31'
        and 'WikibaseCirrusSearch' in ext_deps
    ):
        ext_deps.remove('WikibaseCirrusSearch')

    # Score in REL1_31 doesn't need Wikibase and stuff. Considering they're
    # in somewhat of a mess, it's much easier to just remove them
    if (
        params['ZUUL_PROJECT'] == 'mediawiki/extensions/Score'
        and params['ZUUL_BRANCH'] == 'REL1_31'
    ):
        ext_deps.remove('ArticlePlaceholder')
        ext_deps.remove('PropertySuggester')
        ext_deps.remove('Wikibase')
        ext_deps.remove('WikibaseQualityConstraints')
        ext_deps.remove('WikibaseMediaInfo')
        ext_deps.remove('WikimediaBadges')
        ext_deps.remove('WikibaseLexeme')

    # Export with a literal \n character and have bash expand it later via
    # 'echo -e $XXX_DEPENDENCIES'.
    def glue_deps(prefix, deps):
        return '\\n'.join(
            prefix + d for d in sorted(deps)
        )

    params['SKIN_DEPENDENCIES'] = glue_deps('mediawiki/', skin_deps)
    params['EXT_DEPENDENCIES'] = glue_deps('mediawiki/extensions/', ext_deps)


def get_dependencies(key, mapping, recurse=True):
    """
    Get the full set of dependencies required by an extension

    :param key: extension base name or skin as 'skin/BASENAME'
    :param mapping: mapping of repositories to their dependencies
    :param recurse: Whether to recursively process dependencies
    :return: set of dependencies
    """
    resolved = set()

    def resolve_deps(ext):
        resolved.add(ext)
        deps = set()

        if ext in mapping:
            for dep in mapping[ext]:
                deps.add(dep)

                if recurse and dep not in resolved:
                    deps = deps.union(resolve_deps(dep))

        return deps

    return resolve_deps(key)


tarballextensions = [
    'Cite',
    'CiteThisPage',
    'CodeEditor',
    'ConfirmEdit',
    'Gadgets',
    'ImageMap',
    'InputBox',
    'Interwiki',

    # Skipped, non-trivial (TODO)
    # 'LocalisationUpdate',

    # Skipped, incompatible with other extensions (TODO)
    # 'MultimediaViewer',

    # Skipped, non-trivial (TODO)
    # 'Nuke',

    # Skipped, non-trivial (TODO)
    # 'OATHAuth',

    'ParserFunctions',
    'PdfHandler',
    'Poem',

    # Skipped, non-trivial (TODO)
    # 'Renameuser',
    # 'ReplaceText',

    # 'SecureLinkFixer',

    'SpamBlacklist',

    # Skipped, non-trivial (TODO)
    # 'TitleBlacklist',

    'TemplateData',
    'VisualEditor',

    'WikiEditor',
]

gatedextensions = [
    'AbuseFilter',
    'AntiSpoof',
    'Babel',
    'BetaFeatures',
    'CheckUser',
    'CirrusSearch',
    'cldr',
    'ContentTranslation',
    'Echo',
    'Elastica',
    'EventLogging',
    'EventStreamConfig',
    'FileImporter',
    'Flow',
    'GeoData',
    'GlobalCssJs',
    'GlobalPreferences',
    'GuidedTour',
    'JsonConfig',
    'Kartographer',
    'MobileApp',
    'MobileFrontend',
    'NavigationTiming',
    'SandboxLink',
    'Scribunto',
    'SiteMatrix',
    'TemplateData',
    'Thanks',
    'TimedMediaHandler',
    'Translate',
    'TwoColConflict',
    'UniversalLanguageSelector',
    'VisualEditor',
    'Wikibase',
    'WikibaseCirrusSearch',
    'WikibaseMediaInfo',
    'WikimediaMessages',
]
gatedskins = [
    'MinervaNeue',
    'Vector',
]


def set_gated_extensions(item, job, params):
    deps = []
    skin_deps = []
    # When triggered from the experimental pipeline, add the project to the
    # list of dependencies. Used to inject an extension which is not yet
    # participating.
    if(params['ZUUL_PIPELINE'] == 'experimental'):
        if params['ZUUL_PROJECT'].startswith('mediawiki/extensions/'):
            deps.append(params['ZUUL_PROJECT'].split('/')[-1])
        if params['ZUUL_PROJECT'].startswith('mediawiki/skins/'):
            skin_deps.append(params['ZUUL_PROJECT'].split('/')[-1])

    deps.extend(tarballextensions)

    # Only run gate extensions on non REL1_XX branches
    if not params['ZUUL_BRANCH'].startswith('REL1_'):
        deps.extend(gatedextensions)
        skin_deps.extend(gatedskins)

    deps = sorted(list(set(deps)))
    skin_deps = sorted(list(set(skin_deps)))

    params['EXT_DEPENDENCIES'] = '\\n'.join(
        'mediawiki/extensions/' + dep for dep in deps
    )
    params['SKIN_DEPENDENCIES'] = '\\n'.join(
        'mediawiki/skins/' + skin for skin in skin_deps
    )

    # So we can cd $EXT_NAME && composer test - T161895
    split = params['ZUUL_PROJECT'].split('/')
    if len(split) == 3 and split[1] == 'extensions':
        params['EXT_NAME'] = split[-1]
    if len(split) == 3 and split[1] == 'skins':
        params['SKIN_NAME'] = split[-1]


# Map from ZUUL_PROJECT to DOC_PROJECT
# The default is determined in set_doc_variables
doc_destination = {
    'performance/fresnel': 'fresnel',
    'VisualEditor/VisualEditor': 'visualeditor',
    'oojs/core': 'oojs',
}


def set_doc_variables(item, job, params):
    change = item.change
    doc_subpath = ''

    # ref-updated
    if hasattr(change, 'ref'):
        tag = re.match(r'^refs/tags/(.*)', change.ref)
        if tag:
            # For jobs from Zuul "publish" pipeline,
            # using the "zuul-post" trigger in their Jenkins job.
            # Example value 'refs/tags/v1.2.3' -> 'v1.2.3'
            doc_subpath = tag.group(1)
        else:
            # Branch: 'master'
            doc_subpath = change.ref
    # Changes
    elif hasattr(change, 'refspec'):
        doc_subpath = change.branch

    if doc_subpath:
        params['DOC_SUBPATH'] = doc_subpath

    if 'ZUUL_PROJECT' in params:
        raw_project = params['ZUUL_PROJECT']
        if raw_project in doc_destination:
            # custom names
            raw_project = doc_destination[raw_project]
        elif raw_project.startswith('mediawiki/extensions/'):
            # For MediaWiki extension repos
            raw_project = raw_project.split('/')[-1]

        # Normalize the project name by removing /'s
        params['DOC_PROJECT'] = raw_project.replace('/', '-')

        # @todo Remove DOC_BASENAME once no older mwext- jobs use it.
        params['DOC_BASENAME'] = params['ZUUL_PROJECT'].split('/')[-1]
