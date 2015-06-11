#!/usr/bin/env python3

from collections import defaultdict, OrderedDict
import glob
import os

import lib
import pywikibot

COMPOSER = OrderedDict([
    ('phplint', 'jakub-onderka/php-parallel-lint'),
    ('MW-CS', 'mediawiki/mediawiki-codesniffer'),
])
NPM = OrderedDict([
    ('banana', 'grunt-banana-checker'),
    ('csslint', 'grunt-contrib-csslint'),
    ('jshint', 'grunt-contrib-jshint'),
    ('jsonlint', 'grunt-jsonlint'),
    ('jscs', 'grunt-jscs'),
])

if lib.EXTENSIONS_DIR.startswith('/data/project/ci'):
    lib.update_submodules_and_stuff(lib.EXTENSIONS_DIR)

class Reader:
    def __init__(self):
        self.data = defaultdict(dict)
        self.repos = {}

    def add_repo(self, path, display_name, github_name):
        self.repos[path] = {
            'display': display_name,
            'github': github_name
        }

    def display_repo_name(self, path):
        return '[https://github.com/wikimedia/{github} {display}]'.format(**self.repos[path])

    def read_composer(self, path):
        info = lib.json_load(path)
        if 'require-dev' in info:
            for job in COMPOSER.values():
                version = info['require-dev'].get(job)
                if version:
                    self.data[os.path.dirname(path)][job] = version

    def read_npm(self, path):
        info = lib.json_load(path)
        if 'devDependencies' in info:
            for job in NPM.values():
                version = info['devDependencies'].get(job)
                if version:
                    self.data[os.path.dirname(path)][job] = version

reader = Reader()
composers = glob.glob(lib.EXTENSIONS_DIR + '/*/composer.json')
for composer in composers:
    ext_name = composer.split('/')[-2]
    reader.add_repo(os.path.dirname(composer), 'Extension:%s' % ext_name, 'mediawiki-extensions-%s' % ext_name)
    reader.read_composer(composer)

packages = glob.glob(lib.EXTENSIONS_DIR + '/*/package.json')
for package in packages:
    ext_name = package.split('/')[-2]
    reader.add_repo(os.path.dirname(package), 'Extension:%s' % ext_name, 'mediawiki-extensions-%s' % ext_name)
    reader.read_npm(package)

data = reader.data
# print(data)

header = """
{|class="wikitable"
! Extension
"""
for abbr in list(COMPOSER) + list(NPM):
    header += '! %s\n' % abbr
text = header
for repo_path in sorted(list(data)):
    info = data[repo_path]
    text += '|-\n|%s\n' % reader.display_repo_name(repo_path)
    for job in COMPOSER.values():
        if job in info:
            add = info[job]
            if add == lib.get_packagist_version(job):
                add += '&#x2713;'
        else:
            add = 'n/a'
        text += '|%s\n' % add
    for job in NPM.values():
        if job in info:
            add = info[job]
            if add == lib.get_npm_version(job):
                add += '&#x2713;'
        else:
            add = 'n/a'
        text += '|%s\n' % add
text += '|}'

#print(text)
site = pywikibot.Site('mediawiki', 'mediawiki')
page = pywikibot.Page(site, 'User:Legoktm/ci')
pywikibot.showDiff(page.text, text)
#page.put(text, 'Updating table')
