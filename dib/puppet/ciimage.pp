# ciimage.pp
#
# Use operations/puppet.git classes to build our CI image.

$realm = 'labs'
$labsproject = 'contintcloud'

# Should have run aptconf.pp first.

require_package('git')
# We have jobs compiling native packages for NodeJs, Python, Ruby..
require_package('build-essential')

# Jenkins provision jre by itself but it sounds better to have it already in
# the  image. T126246.
include jenkins::slave::requisites

include contint::slave_scripts
include contint::packages::base
include contint::composer
include contint::php
if os_version('ubuntu >= trusty') {
    # We dont run PHP based jobs on Jessie yet since we match Wikimedia
    # production which has MediaWiki running on Trusty.
    # Jessie lacks php5-fss T95002. PHP is provided via HHVM.
    include mediawiki::packages::php5
}
package { 'cron':
    ensure => present,
    before => Class['contint::hhvm'],
}
include contint::hhvm

include contint::packages::javascript
include contint::packages::php
require_package('php5-xhprof')
exec { 'Enable PHP module xhprof':
    command     => '/usr/sbin/php5enmod -s ALL xhprof',
    subscribe   => Package['php5-xhprof'],
    refreshonly => true,
}

# Qunit/Selenium related
include contint::browsers
class { 'contint::worker_localhost':
    owner => 'jenkins',
}
# Augeas rule deals with /etc/logrotate.d/apache2
# Sent to puppet.git https://gerrit.wikimedia.org/r/#/c/291024/
Package['apache2'] ~> Augeas['Apache2 logs']
exec { 'prevent apache2 from executing':
  refreshonly => true,
  command     => '/bin/chmod -x /usr/sbin/apache2',
  onlyif      => '/bin/bash -c "export | grep DIB_"',
  subscribe   => Package['apache2'],
  before      => [
    Service['apache2'],
    Exec['apache2_hard_restart'],
  ],
  after       => [
    Exec['apache2_test_config_and_restart'],
  ],
}
if os_version('ubuntu == trusty') {
  exec { 'create /run/apache2':
    command => '/bin/mkdir -p /run/apache2',
    before  => Exec['apache2_test_config_and_restart'],
  }
}

stage { 'last': }
Stage['main'] -> Stage['last']

class apache2_allow_execution {
  exec { 'allow apache2 execution':
      command => '/bin/chmod +x /usr/sbin/apache2',
  }
}
class { 'apache2_allow_execution':
    stage => last,
}

require_package('libimage-exiftool-perl')
# MediaWiki has $wgDjvuPostProcessor = 'pnmtojpeg';
# Provided by netpbm which is in imagemagick Recommends
require_package('netpbm')
include ::imagemagick::install

# From mediawiki::packages (which we do not want because of texlive)
require_package('djvulibre-bin')

include contint::packages::ruby

# Lot of npm based jobs rely on jsduck...
if os_version('ubuntu == trusty') {
    # We have build a Debian package
    package { 'ruby-jsduck':
        ensure => present,
    }
}
# Install from gem
if os_version('debian >= jessie') {
    package { 'jsduck':
        ensure          => present,
        provider        => 'gem',
        require         => [
            Class['::contint::packages::ruby'],
            Package['build-essential'],
        ],
    }
}

if os_version('debian >= jessie') {
    include contint::packages::python
    include contint::browsers

    # services packages and -dev packages for npm modules compilation and test
    # run. NOTE: hiera must have: service::configuration::use_dev_pkgs: true
    include graphoid::packages
    include mathoid::packages
}

ensure_packages(['mariadb-client', 'mariadb-server'])

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
