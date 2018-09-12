from collections import OrderedDict
import os
import unittest

from nose.plugins.attrib import attr


# Import function
param_func_env = {}
execfile(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../zuul/parameter_functions.py'),
    param_func_env)

gatedextensions = param_func_env['gatedextensions']
get_dependencies = param_func_env['get_dependencies']
all_dependencies = param_func_env['dependencies']

test = unittest.TestCase('__init__')

# Retrieve dependencies of each of the gated projects
gated_deps = OrderedDict()
for gated_project in gatedextensions:
    gated_deps[gated_project] = get_dependencies(
        gated_project, all_dependencies)


@attr('qa')
def test_deps_of_gated_are_in_gate():
    for (project, its_deps) in gated_deps.items():
        for its_dep in sorted(its_deps):
            test.assertIn.__func__.description = (
                '%s dependency %s is in gate' % (project, its_dep))
            yield (
                test.assertIn,
                its_dep, set(gatedextensions),
                '%s depends on %s but it is not in the gate' % (
                    project, its_dep))
    del(test.assertIn.__func__.description)
