import argparse
from collections import defaultdict
import logging
import json
import os
import sys

from docker_pkg.builder import DockerBuilder
from docker_pkg import dockerfile

logging.basicConfig()
log = logging.getLogger('list')
log.setLevel(logging.INFO)

argparser = argparse.ArgumentParser()
argparser.add_argument('--debug', action='store_true')
options = argparser.parse_args()
if options.debug:
    log.setLevel(logging.DEBUG)
    log.debug('Logging at debug level')

base_dir = os.path.dirname(os.path.realpath(__file__))

dockerfile.TemplateEngine.setup({}, [])
build = DockerBuilder(base_dir, {})

build.scan()
images = build.all_images

# Preseed some dependencies which are not properly defined
# parent -> child
edges = set([
    ('scratch', 'docker-registry.wikimedia.org/wikimedia-jessie'),
    ('docker-registry.wikimedia.org/wikimedia-jessie', 'ci-jessie'),
    ('scratch', 'docker-registry.wikimedia.org/wikimedia-stretch'),
    ('docker-registry.wikimedia.org/wikimedia-stretch', 'ci-stretch'),
])
cibaseimage = {e[1] for e in edges}

# Add dependencies from our control files
for image in images:
    short_name = image.image.short_name
    depends = image.image.depends

    if not depends:
        edges.add(('scratch', short_name))
        continue

    for dep in depends:
        edges.add((dep, short_name))


def buildtree(edges):
    # A beautiful solution by Ting-Yu Lin
    # aethanyc 2014-01-08 https://gist.github.com/aethanyc/8313640

    tree = defaultdict(dict)

    for parent, child in edges:
        log.debug(
            'Edge: parent {parent} -> child {child}'.format_map(locals()))
        tree[parent][child] = tree[child]

    parents, children = zip(*edges)
    roots = set(parents).difference(children)

    return {root: tree[root] for root in roots}


tree = buildtree(edges)

baseimages = {i for i in tree['scratch'].keys()}
lack_deps = baseimages.difference(cibaseimage)
for image in lack_deps:
    log.warn('Depends is not set in %s/control' % image)

print(json.dumps(tree, indent=4))

print('Edges:')
errors = []
for image in images:
    # image is a docker_pkg.image.DockerImage object
    short_name = image.image.short_name
    tag = image.image.tag
    depends = image.image.depends

    for dep in depends:
        print('"%s" -> "%s"' % (dep, short_name))
    if not depends and short_name not in cibaseimage:
        errors.append(short_name)

if errors:
    print('--- Errors ---')
    for error in errors:
        print('%s lacks Depends: field in control file' % error)
    sys.exit(1)
