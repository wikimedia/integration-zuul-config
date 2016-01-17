#!/usr/bin/env python2

dependencies = {
    'AbuseFilter': ['AntiSpoof'],
    'ApiFeatureUsage': ['Elastica'],
    'ArticlePlaceholder': ['Wikibase', 'Scribunto'],
    'Capiunto': ['Scribunto'],
    'Citoid': ['VisualEditor'],
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
    'Wikibase': ['cldr', 'Elastica', 'GeoData', 'Scribunto',
                 'Capiunto'],
    'Wikidata': ['cldr', 'Elastica', 'GeoData', 'Scribunto'],
    'WikidataPageBanner': ['Wikidata'],
    'WikimediaBadges': ['Wikibase'],
    'WikimediaPageViewInfo': ['Graph'],
}

# Limit execution to these jobs
jobs = ('mwext-testextension', 'mwext-qunit', 'mwext-mw-selenium')


def set_ext_dependencies(item, job, params):
    """
    Reads dependencies from the yaml file and adds them as a parameter
    :type item: zuul.model.QueueItem
    :type job: zuul.model.Job
    :type params: dict
    """
    if not job.name.startswith(jobs):
        return

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
    deps = set()
    if ext_name in mapping:
        for dep in mapping[ext_name]:
            deps.add(dep)
            # TODO: Max recursion limit?
            deps = deps.union(get_dependencies(dep, mapping))
    return deps
