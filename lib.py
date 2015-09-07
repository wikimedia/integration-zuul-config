#!/usr/bin/env python3

import codecs
import functools
import json
import os
import requests
import subprocess
import tempfile

s = requests.session()

@functools.lru_cache()
def get_npm_version(package):
    r = s.get('https://registry.npmjs.org/%s' % package)
    version = r.json()['dist-tags']['latest']
    print('Latest %s: %s' % (package, version))
    return version

@functools.lru_cache()
def get_packagist_version(package):
    r = s.get('https://packagist.org/packages/%s.json' % package)
    resp = r.json()['package']['versions']
    normalized = set()
    for ver in resp:
        if not ver.startswith('dev-'):
            if ver.startswith('v'):
                normalized.add(ver[1:])
            else:
                normalized.add(ver)
    version = max(normalized)
    print('Latest %s: %s' % (package, version))
    return version

def commit_and_push(files, msg, branch, topic, push=True):
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(bytes(msg, 'utf-8'))
    f.close()
    subprocess.check_call(['git', 'add'] + files)
    subprocess.check_call(['git', 'commit', '-F', f.name])
    push_cmd = ['git', 'push', 'gerrit', 'HEAD:refs/for/{0}%topic={1}'.format(branch, topic)]
    if push:
        subprocess.check_call(push_cmd)
    else:
        print(' '.join(push_cmd))
    os.unlink(f.name)

if os.path.isdir('/data/project/ci'):
    # Running on Tool labs
    ON_LABS = True
    EXTENSIONS_DIR = '/data/project/ci/src/extensions'
    SKINS_DIR = '/data/project/ci/src/skins'
    SRC = '/data/project/ci/src'
    MEDIAWIKI_DIR = '/data/project/ci/src/mediawiki'
else:
    # Legoktm's laptop
    ON_LABS = False
    EXTENSIONS_DIR = '/home/km/projects/vagrant/mediawiki/extensions'
    SKINS_DIR = '/home/km/projects/vagrant/mediawiki/skins'
    SRC = '/home/km/projects'
    MEDIAWIKI_DIR = '/home/km/projects/vagrant/mediawiki'


def git_pull(path, update_submodule=False):
    subprocess.check_call(['git', '-C', path, 'pull'])
    if update_submodule:
        subprocess.check_call(['git', '-C', path, 'submodule', 'update',
                               '--init'])

def json_load(path):
    with codecs.open(path, 'r', 'utf-8') as f:
        info = json.loads(f.read())
    return info

@functools.lru_cache()
def get_wmf_deployed_list():
    r = requests.get('https://phabricator.wikimedia.org/diffusion/MREL/browse/master/make-wmf-branch/config.json?view=raw')
    conf = r.json()
    repos = set()
    for ext in conf['extensions']:
        repos.add('mediawiki-extensions-' + ext)
    for skin in conf['skins']:
        repos.add('mediawiki-skins-' + skin)
    # Intentionally ignore special_extensions because they're special
    return repos

def is_wmf_deployed(github_name):
    return github_name in get_wmf_deployed_list()
