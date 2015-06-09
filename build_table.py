#!/usr/bin/env python3

from collections import defaultdict, OrderedDict
import glob
import json

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

EXTENSIONS_DIR = '/home/km/projects/vagrant/mediawiki/extensions'

data = defaultdict(dict)
composers = glob.glob(EXTENSIONS_DIR + '/*/composer.json')
for composer in composers:
    ext_name = composer.split('/')[-2]
    with open(composer) as f:
        info = json.load(f)
        if 'require-dev' in info:
            for job in COMPOSER.values():
                version = info['require-dev'].get(job)
                if version:
                    data[ext_name][job] = version

packages = glob.glob(EXTENSIONS_DIR + '/*/package.json')
for package in packages:
    ext_name = package.split('/')[-2]
    with open(package) as f:
        info = json.load(f)
        if 'devDependencies' in info:
            for job in NPM.values():
                version = info['devDependencies'].get(job)
                if version:
                    data[ext_name][job] = version


# print(data)

header = """
{|class="wikitable"
! Extension
"""
for abbr in list(COMPOSER) + list(NPM):
    header += '! %s\n' % abbr
text = header
for ext_name in sorted(list(data)):
    info = data[ext_name]
    text += '|-\n|%s\n' % ext_name
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
text += '|}\n'

#print(text)
site = pywikibot.Site('mediawiki', 'mediawiki')
page = pywikibot.Page(site, 'User:Legoktm/ci')
pywikibot.showDiff(page.text, text)
#page.put(text, 'Updating table')
