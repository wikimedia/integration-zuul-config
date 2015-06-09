#!/usr/bin/env python3

import functools
import os
import requests
import subprocess
import tempfile

@functools.lru_cache()
def get_npm_version(package):
    r = requests.get('https://registry.npmjs.org/%s' % package)
    return r.json()['dist-tags']['latest']

@functools.lru_cache()
def get_packagist_version(package):
    r = requests.get('https://packagist.org/packages/%s.json' % package)
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

def commit_and_push(files, msg, branch, topic):
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(bytes(msg, 'utf-8'))
    f.close()
    subprocess.check_call(['git', 'add'] + files)
    subprocess.check_call(['git', 'commit', '-F', f.name])
    subprocess.check_call(['git', 'push', 'gerrit', 'HEAD:refs/for/{0}%topic={1}'.format(branch, topic)])
    os.unlink(f.name)
