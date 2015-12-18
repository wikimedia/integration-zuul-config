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
    stage  => first,
    # Refreshing a snapshot should update repos as well
    notify => Exec['apt-get update'],
}

include contint::packages::base
include contint::packages::javascript
include contint::packages::python
include contint::packages::ruby

package { 'zuul':
  ensure => present,
}

# Should be include contint::packages::ops once GeoIP is installable
package { ['etcd', 'python-etcd']:
    ensure => present,
}
