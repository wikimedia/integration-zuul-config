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
