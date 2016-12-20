#!/usr/bin/env python2
"""
Usage:

* Install fabric (<http://www.fabfile.org/>) via
  pip install --user fabric or a virtualenv
* Configure your .ssh/config so it can
  access contint1001.wikimedia.org and uses
  the proper username and key.
* Run $ fab deploy_zuul

"""
from fabric.api import *  # noqa
from fabric.contrib.console import confirm

env.sudo_prefix = 'sudo -ni '
env.use_ssh_config = True


@task
def deploy_zuul():
    """Deploy a Zuul layout change"""
    env.sudo_user = 'zuul'
    env.host_string = 'contint1001.wikimedia.org'

    with cd('/etc/zuul/wikimedia'):
        sudo('git remote update')
        sudo('git --no-pager log -p HEAD..origin/master zuul')
        if confirm('Does the diff look good?') and confirm(
                'Did you log your reload in #wikimedia-releng (e.g. "!log Reloading' +
                ' Zuul to deploy [hash]")'):
            sudo('git rebase')
            sudo('/etc/init.d/zuul reload')


@task
def deploy_slave_scripts():
    """Pull integration/jenkins on CI labs slaves"""
    env.sudo_user = 'root'
    env.host_string = 'integration-saltmaster.integration.eqiad.wmflabs'
    sudo("salt -v '*slave*' cmd.run "
         "'cd /srv/deployment/integration/slave-scripts && git pull'")


@task(default=True)
def help():
    """Usage and list of commands"""
    from fabric.main import show_commands
    show_commands(__doc__, 'normal')
