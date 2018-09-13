import os
import unittest

from nose.plugins.attrib import attr


# Import function
param_func_env = {}
execfile(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../zuul/parameter_functions.py'),
    param_func_env)


class GatedExtensions(set):
    def __repr__(self):
        return "<gated extensions>"

    def __str__(self):
        return "<gated extensions>"


gatedextensions = GatedExtensions(param_func_env['gatedextensions'])
get_dependencies = param_func_env['get_dependencies']
all_dependencies = param_func_env['dependencies']

test = unittest.TestCase('__init__')

# Retrieve dependencies of each projects and keep track of the gated project
# that depends on it.
gated_deps = {}
for gated_project in gatedextensions:
    deps = get_dependencies(gated_project, all_dependencies)
    for dep in deps:
        if dep not in gated_deps:
            gated_deps[dep] = [gated_project]
        else:
            gated_deps[dep].append(gated_project)


@attr('qa')
def test_deps_of_gated_are_in_gate():
    for (gated_dep, origin) in sorted(gated_deps.iteritems()):
        test.assertIn.__func__.description = (
            'Dependency of gated project is in gate: %s' % (gated_dep))
        yield (
            test.assertIn,
            gated_dep, gatedextensions,
            '%s must be in gate since it is a dependency of: %s' % (
                gated_dep, ', '.join(origin)))
    del(test.assertIn.__func__.description)
