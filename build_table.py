#!/usr/bin/env python3

from collections import defaultdict, OrderedDict
import glob
import os

import lib
import pywikibot
import zuul_output_reader

COMPOSER = OrderedDict([
    ('phplint', 'jakub-onderka/php-parallel-lint'),
    ('phpunit', 'phpunit/phpunit'),
    ('MW-CS', 'mediawiki/mediawiki-codesniffer'),
])
NPM = OrderedDict([
    ('banana', 'grunt-banana-checker'),
    ('csslint', 'grunt-contrib-csslint'),
    ('jshint', 'grunt-contrib-jshint'),
    ('jsonlint', 'grunt-jsonlint'),
    ('jscs', 'grunt-jscs'),
])


class Reader:
    def __init__(self):
        self.data = defaultdict(lambda: defaultdict(dict))
        self.repos = {}

    def add_repo(self, display_name, github_name):
        self.repos[github_name] = {
            'display': display_name,
            'github': github_name
        }

    def display_repo_name(self, path):
        info = self.repos[path]
        text = '[https://github.com/wikimedia/{github} {display}]'.format(
               **info)
        if lib.is_wmf_deployed(info['github']):
            text += ' (WMF-deployed)'
        return text

    def read_composer(self, path, github_name):
        info = lib.json_load(path)
        if 'require-dev' in info:
            for job in COMPOSER.values():
                version = info['require-dev'].get(job)
                if version:
                    self.data[github_name][job]['version'] = version

    def read_npm(self, path, github_name):
        info = lib.json_load(path)
        if 'devDependencies' in info:
            for job in NPM.values():
                version = info['devDependencies'].get(job)
                if version:
                    self.data[github_name][job]['version'] = version

    def read_zuul(self, info, github_name):
        #if github_name != 'mediawiki-extensions-Echo':
        #    return
        if any(info.get(x) if x.endswith('npm') else False for x in info):
            for job_name in list(NPM.values()):
                #print(job_name)
                if job_name in self.data[github_name]:
                    #print('found')
                    self.data[github_name][job_name]['color'] = 'lightgreen'
        if any(info.get(x) if x.startswith('php-composer-test') else False for x in info):  # noqa
            for job_name in list(COMPOSER.values()):
                #print(job_name)
                if job_name in self.data[github_name]:
                    #print('found')
                    self.data[github_name][job_name]['color'] = 'lightgreen'
        for job, voting in info.items():
            color = 'lightgreen' if voting else 'red'
            if job in COMPOSER:
                real_jobs = [COMPOSER[job]]
            elif job in NPM:
                real_jobs = [NPM[job]]
            elif 'testextension' in job:
                real_jobs = [COMPOSER['phpunit']]
            elif job.endswith('-jslint'):
                real_jobs = [NPM['jshint'], NPM['jsonlint']]
            else:
                continue
            for job in real_jobs:
                if job not in self.data[github_name]:
                    self.data[github_name][job] = {
                        'version': 'Jenkins',
                        'color': color
                    }


reader = Reader()


OTHER_STUFF = [
    'AhoCorasick',
    'at-ease',
    'cdb',
    'IPSet',
    'oojs',
    'oojs-ui',
    'utfnormal',
    'VisualEditor',
]

if lib.ON_LABS:
    lib.git_pull(lib.EXTENSIONS_DIR, update_submodule=True)
    lib.git_pull(lib.SKINS_DIR, update_submodule=True)
    lib.git_pull(lib.MEDIAWIKI_DIR)

reader.add_repo('MediaWiki core', 'mediawiki')

composer_paths = {'mediawiki': lib.MEDIAWIKI_DIR + '/' + 'composer.json'}
package_paths = {'mediawiki': lib.MEDIAWIKI_DIR + '/' + 'package.json'}

for repo in OTHER_STUFF:
    path = lib.SRC + '/' + repo
    if lib.ON_LABS:
        lib.git_pull(path)
    reader.add_repo(repo, repo)
    composer = path + '/' + 'composer.json'
    package = path + '/' + 'package.json'
    if os.path.exists(composer):
        composer_paths[repo] = composer
    if os.path.exists(package):
        package_paths[repo] = package

for repo_type, glob_path in {'Extension': lib.EXTENSIONS_DIR,
                             'Skin': lib.SKINS_DIR}.items():
    composers = glob.glob(glob_path + '/*/composer.json')
    repo_name = lambda x: 'mediawiki-%s-%s' % (repo_type.lower() + 's', x)
    for composer in composers:
        ext_name = composer.split('/')[-2]
        repo = repo_name(ext_name)
        reader.add_repo(repo_type + ':%s' % ext_name, repo)
        composer_paths[repo] = composer

    for repo, path in composer_paths.items():
        reader.read_composer(path, repo)

    packages = glob.glob(glob_path + '/*/package.json')
    for package in packages:
        ext_name = package.split('/')[-2]
        repo = repo_name(ext_name)
        reader.add_repo(repo_type + ':%s' % ext_name, repo)
        package_paths[repo] = package

    for repo, path in package_paths.items():
        reader.read_npm(path, repo)

zuul_data = zuul_output_reader.main()
for repo, info in zuul_data.items():
    if repo.startswith('mediawiki-extensions'):
        prefix = 'Extension:'
    else:
        prefix = 'Skin:'

    reader.add_repo(prefix + repo.split('-')[-1], repo)
    reader.read_zuul(info, repo)

data = reader.data
# print(data)

header = """
{{/Header}}
{|class="wikitable sortable"
! rowspan="2" |Extension
! colspan="%s" |composer
! colspan="%s" |npm
|-
""" % (len(COMPOSER), len(NPM))
for abbr in list(COMPOSER) + list(NPM):
    header += '! %s\n' % abbr
text = header
# hack to make MediaWiki come first
paths = list(sorted(data))
paths.remove('mediawiki')
paths = ['mediawiki'] + paths
for repo_path in paths:
    #if repo_path != 'mediawiki-extensions-Echo':
    #    continue
    info = data[repo_path]
    text += '|-\n|%s\n' % reader.display_repo_name(repo_path)
    for job in COMPOSER.values():
        color = ''
        if job in info:
            color = info[job].get('color')
            if color:
                color = 'style="background-color: %s" |' % color
            else:
                color = ''
            add = info[job]['version']
            if add == lib.get_packagist_version(job):
                add += '&#x2713;'
        else:
            add = 'n/a'
        text += '|%s\n' % (color + add)

    for job in NPM.values():
        color = ''
        if job in info:
            color = info[job].get('color')
            if color:
                color = 'style="background-color: %s" |' % color
            else:
                color = ''
            add = info[job]['version']
            if add == lib.get_npm_version(job):
                add += '&#x2713;'
        else:
            add = 'n/a'
        text += '|%s\n' % (color + add)
text += '|}'

#print(text)
site = pywikibot.Site('mediawiki', 'mediawiki')
page = pywikibot.Page(site, 'User:Legoktm/ci')
pywikibot.showDiff(page.text, text)
if lib.ON_LABS:
    page.put(text, 'Updating table')
