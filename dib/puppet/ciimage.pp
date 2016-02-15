# ciimage.pp
#
# Use operations/puppet.git classes to build our CI image.

$realm = 'labs'

# Needs ::apt first so we get jessie-wikimedia and jessie-backports configured
# and pinned. Else our packages are not up-to-date / not found.
stage { 'first':
    before => Stage['main'],
}
class { '::apt':
    stage => first,
}

# Jenkins provision jre by itself but it sounds better to have it already in
# the  image. T126246.
include jenkins::slave::requisites

# Slave scripts
exec { 'recursive mkdir of /srv/deployment/integration':
    command => '/bin/mkdir -p /srv/deployment/integration',
    creates => '/srv/deployment/integration',
}

# Inject slave scripts
#
# We can't reuse contint::slave_scripts which grab unrelated repositories and
# symlink composer.
# This is done via puppet rather than in dib so new snapshot images get
# slave-scripts refreshed.
require_package('git')
git::clone { 'jenkins CI slave scripts':
    ensure             => 'latest',
    directory          => '/srv/deployment/integration/slave-scripts',
    origin             => 'https://gerrit.wikimedia.org/r/p/integration/jenkins.git',
    recurse_submodules => true,
    require            => Exec['recursive mkdir of /srv/deployment/integration'],
}

include contint::packages::base
include contint::packages::python
include contint::packages::ruby

# Broken beyond repair
#include contint::packages::javascript

package { [
    'nodejs',
    'nodejs-legacy',
    'npm',
    ]:
    ensure => present,
}

# FIXME should be upstreamed to operations/puppet.git as contint::packages::dev
package { [
    'pkg-config',
    ]:
    ensure => present,
}

ensure_packages(['openjdk-7-jre-headless'])

package { 'zuul':
  ensure => present,
}

# Should be include contint::packages::ops once GeoIP is installable
package { ['etcd', 'python-etcd']:
    ensure => present,
}
