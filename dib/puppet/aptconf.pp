$realm = 'labs'
$labsproject = 'contintcloud'

require_package('apt-transport-https')

# dib deletes /etc/apt/sources.list however our apt::repository for
# jessie-backports attempts to comment out old lines from it.
#
# Should be fixed by https://gerrit.wikimedia.org/r/#/c/325570/
#
exec { 'Ensure sources.list exists':
    command => '/usr/bin/touch /etc/apt/sources.list',
    creates => '/etc/apt/sources.list',
    before  => Class['::apt'],
}

class { '::apt': }
include contint::packages::apt
