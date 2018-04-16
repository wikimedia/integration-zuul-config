#!/usr/bin/env python2
"""
Usage:

* Install fabric (<http://www.fabfile.org/>) via
  pip install --user fabric or a virtualenv
* Configure your .ssh/config so it can
  access the following hosts and uses
  the proper username and key:
   - contint1001.wikimedia.org
   - integration-cumin.integration.eqiad.wmflabs
* Run $ fab deploy_zuul

"""
from fabric.api import *  # noqa
from fabric.contrib.console import confirm

env.sudo_prefix = 'sudo -H '
env.use_ssh_config = True


def _update_integration_config(
        diff_dir='zuul', log_msg='Reloading Zuul to deploy [url]'):
    with settings(sudo_user='zuul'):
        with cd('/etc/zuul/wikimedia'):
            sudo('git remote update')
            sudo('git --no-pager log -p HEAD..origin/master {}'.format(
                diff_dir))
            if confirm('Does the diff look good?') and confirm(
                    'Did you log your reload in #wikimedia-releng (e.g. ' +
                    '"!log {}")'.format(log_msg)):
                sudo('git rebase')
                sudo('git -c gc.auto=128 gc --auto --quiet')

                return True

    return False


@task
def deploy_docker():
    """Update docker-pkg built images"""
    env.host_string = 'contint1001.wikimedia.org'

    updated = _update_integration_config(
        diff_dir='dockerfiles',
        log_msg='Updating docker-pkg files on contint1001 for [url]'
    )

    if not updated:
        return

    with cd('/tmp'):
        docker_pkg = '/srv/deployment/docker-pkg/venv/bin/docker-pkg'
        docker_pkg_config = '/etc/docker-pkg/integration.yaml'
        dockerfiles = '/etc/zuul/wikimedia/dockerfiles'
        cmd = '{} -c {} {}'.format(
            docker_pkg, docker_pkg_config, dockerfiles)

        run(cmd)

        run('cat /tmp/docker-pkg-build.log')

        if confirm('delete build log?'):
            run('rm /tmp/docker-pkg-build.log')


@task
def deploy_zuul():
    """Deploy a Zuul layout change"""
    env.host_string = 'contint1001.wikimedia.org'

    if _update_integration_config():
        with settings(sudo_user='root'):
            sudo('/usr/sbin/service zuul reload', shell=False)


@task
def deploy_slave_scripts():
    """Pull integration/jenkins on CI labs slaves"""
    with settings(sudo_user='root'):
        env.host_string = 'integration-cumin.integration.eqiad.wmflabs'
        sudo("cumin --force 'name:\"slave-(?!docker|.*android)\"' "
             "'cd /srv/deployment/integration/slave-scripts && git pull'")


@task
def docker_pull_image(imageName):
    """Pull a docker image onto the docker slaves"""
    with settings(sudo_user='root'):
        env.host_string = 'integration-cumin.integration.eqiad.wmflabs'
        sudo("cumin --force 'name:slave-docker' "
             "'docker pull " + imageName + "'")


@task(default=True)
def help():
    """Usage and list of commands"""
    from fabric.main import show_commands
    show_commands(__doc__, 'normal')
