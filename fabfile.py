#!/usr/bin/env python2
"""
Usage:

* Install fabric (<http://www.fabfile.org/>) via
  pip install --user fabric or a virtualenv
* Configure your .ssh/config so it can
  access gallium.wikimedia.org and uses the
  proper username and key.
* Run $ fab deploy_zuul

"""
from fabric.api import *  # noqa
from fabric.contrib.console import confirm

env.hosts = ['gallium.wikimedia.org']
env.sudo_user = 'zuul'
env.sudo_prefix = 'sudo -ni '
env.use_ssh_config = True


@task
def deploy_zuul():
    with cd('/etc/zuul/wikimedia'):
        sudo('git remote update')
        sudo('git --no-pager log -p HEAD..origin/master zuul')
        if confirm('Does the diff look good?') and confirm('Log your reload' +
          ' in #wikimedia-releng (e.g. "!log Reloading Zuul to deploy [hash]")'
        ):
            sudo('git rebase')
            sudo('/etc/init.d/zuul reload')
