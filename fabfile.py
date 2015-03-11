#!/usr/bin/env python2
"""
Usage:

* Install fabric (<http://www.fabfile.org/>)
* Configure your .ssh/config to have zuul.eqiad.wmnet point
  to gallium and use your expected username and ssh key.
* Run $ fab deploy_zuul

"""
from fabric.api import *  # noqa
from fabric.contrib.console import confirm

env.hosts = ['zuul.eqiad.wmnet']
env.sudo_user = 'zuul'
env.sudo_prefix = 'sudo -ni '
env.use_ssh_config = True


@task
def deploy_zuul():
    with cd('/etc/zuul/wikimedia'):
        sudo('git remote update')
        sudo('git --no-pager log -p HEAD..origin/master zuul')
        if confirm('Does the diff look good?'):
            sudo('git rebase')
            sudo('/etc/init.d/zuul reload')
