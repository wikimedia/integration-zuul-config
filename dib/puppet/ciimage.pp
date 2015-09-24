# ciimage.pp
#
# Use operations/puppet.git classes to build our CI image.

# Needs ::apt first so we get jessie-wikimedia and jessie-backports configured
# and pinned. Else our packages are not up-to-date / not found.
stage { 'first':
    before => Stage['main'],
}
class { '::apt':
    stage => first,
}

include contint::packages::base
include contint::packages::python

# Should be include contint::packages::ops once GeoIP is installable
package { 'etcd':
    ensure => present,
}
