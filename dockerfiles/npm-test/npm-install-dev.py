#!/usr/bin/env python


# npm-install-dev.py
# ------------------
#
# Installs the development dependencies for Node.JS services. To use it,
# simply start it in the directory where your package.json file is
# located. Note that it assumes the production node module dependencies
# have already been installed, i.e. it does not check they are present.


import json
import os
import sys
import subprocess


deps = dict()
cwd = os.getcwd()
src_dir = os.environ.get('NPM_SET_PATH', 'src').replace('./', '')
full_src = cwd + '/' + src_dir
config = full_src + '/config.dev.yaml'
mod_path = full_src + '/app.js'


print('[*] NPM devDependencies Installation [*]')

with open(cwd + '/package.json') as fd:
    pkg_info = json.load(fd)
    if 'devDependencies' in pkg_info:
        deps = pkg_info['devDependencies']

for pkg in iter(deps):
    print('[*] - Installing ' + pkg + ' ...')
    subprocess.check_call(
        ['npm', 'install', pkg + '@' + deps[pkg]],
        stdout=sys.stdout, stderr=sys.stdout
    )

if os.path.exists(config):
    print('[*] Fixing up the server config to run in CI ...')
    subprocess.check_call([
        'sed',
        '-i',
        '-e',
        's/module: .\\/app.js/module: ' + mod_path.replace('/', '\\/') + '/g',
        config
    ])

print('[*] NPM devDependencies Done [*]')
