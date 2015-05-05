#!/usr/bin/env python2

dependencies = {
    'AbuseFilter': ['AntiSpoof'],
    'ApiFeatureUsage': ['Elastica'],
    'Capiunto': ['Scribunto'],
    'Citoid': ['VisualEditor'],
    'CodeEditor': ['WikiEditor'],
    'Flow': ['AbuseFilter', 'CheckUser', 'ConfirmEdit', 'Mantle',
             'MobileFrontend', 'SpamBlacklist', 'Echo', 'EventLogging',
             'VisualEditor'],
    'Thanks': ['Echo', 'Flow'],
    'VectorBeta': ['EventLogging'],
}


def set_ext_dependencies(item, job, params):
    """
    Reads dependencies from the yaml file and adds them as a parameter
    :type item: zuul.model.QueueItem
    :type job: zuul.model.Job
    :type params: dict
    """
    if not job.name.startswith(('mwext-testextension', 'mwext-qunit')):
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
