# ciimage.pp
#
# Use operations/puppet.git classes to build our CI image.

$realm = 'labs'
$labsproject = 'contintcloud'

# Should have run aptconf.pp first.

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

include contint::composer
include contint::php
if os_version('ubuntu >= trusty') {
    # We dont run PHP based jobs on Jessie yet since we match Wikimedia
    # production which has MediaWiki running on Trusty.
    include mediawiki::packages::php5
} elsif os_version('debian >= jessie') {
    package { 'cron':
        ensure => present,
        before => Class['contint::hhvm'],
    }
    # Lack php5-fss T95002. Provide PHP via HHVM for now.
    include contint::hhvm
}

if os_version('debian >= jessie') {
    include contint::packages::javascript
    include contint::packages::python
    include contint::packages::ruby
    include contint::browsers

    # services packages and -dev packages for npm modules compilation and test
    # run. NOTE: hiera must have: service::configuration::use_dev_pkgs: true
    include graphoid::packages
    include mathoid::packages
}

# FIXME should be upstreamed to operations/puppet.git as contint::packages::dev
package { [
    'pkg-config',
    ]:
    ensure => present,
}

# For mediawiki/extensions/Collection/OfflineContentGenerator/bundler
ensure_packages(['zip', 'unzip'])

ensure_packages(['openjdk-7-jre-headless'])

package { 'zuul':
  ensure => present,
}

if os_version('debian >= jessie') {
    # Following should later be included in contint::packages::ops once GeoIP
    # is installable.
    package { ['etcd', 'python-etcd']:
        ensure => present,
    }

    # We run varnishtest
    package { 'varnish':
        ensure => present,
    }
}
# end contint::packages::ops
