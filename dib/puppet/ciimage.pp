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

include mediawiki::packages::php5

package { 'cron':
    ensure => present,
    before => Class['contint::hhvm'],
}
include contint::hhvm

include contint::packages::javascript
include apt
include contint::packages::apt
include contint::packages::php

require_package('arcanist')

require_package('php5-xhprof')
exec { 'Enable PHP module xhprof':
    command     => '/usr/sbin/php5enmod -s ALL xhprof',
    subscribe   => Package['php5-xhprof'],
    refreshonly => true,
}

require_package('libimage-exiftool-perl')
# MediaWiki has $wgDjvuPostProcessor = 'pnmtojpeg';
# Provided by netpbm which is in imagemagick Recommends
require_package('netpbm')
include ::imagemagick::install

# From mediawiki::packages (which we do not want because of texlive)
require_package('djvulibre-bin')

include contint::packages::ruby

# Install from gem
if os_version('debian >= jessie') {
    package { 'jsduck':
        ensure   => present,
        provider => 'gem',
        require  => [
            Class['::contint::packages::ruby'],
            Package['build-essential'],
        ],
    }
}

# Overrides
class standard {

}
define diamond::collector(
  $settings    = undef,
  $ensure      = present,
  $source      = undef,
  $content     = undef,
) {

}

# allow apache2 execution
class apache2_allow_execution {
  exec { 'allow apache2 execution':
      command => '/bin/chmod +x /usr/sbin/apache2',
  }
}
if os_version('debian >= jessie') {
    include contint::packages::doxygen
    include contint::packages::java
    include contint::packages::python

    # Qunit/Selenium related
    include contint::browsers


    # FIXME: hack, our manifests no more ship libapache2-mod-php5
    # See T144802
    include ::apache::mod::php5

    # For Selenium jobs video recording (T113520)
    require_package('libav-tools')

    class { 'contint::worker_localhost':
        owner => 'jenkins',
    }

    # Augeas rule deals with /etc/logrotate.d/apache2
    # Sent to puppet.git https://gerrit.wikimedia.org/r/#/c/291024/
    Package['apache2'] ~> Augeas['Apache2 logs']

    # Nasty workaround when running inside a chroot...
    exec { 'prevent apache2 from executing':
      refreshonly => true,
      command     => '/bin/chmod -x /usr/sbin/apache2',
      onlyif      => '/bin/bash -c "export | grep DIB_"',
      subscribe   => Package['apache2'],
      before      => [
        Service['apache2'],
        Exec['apache2_hard_restart'],
      ],
      require     => [
        Exec['apache2_test_config_and_restart'],
      ],
    }

    stage { 'last': }
    Stage['main'] -> Stage['last']

    class { 'apache2_allow_execution':
        stage => last,
    }

    # services packages and -dev packages for npm modules compilation and test
    # run. NOTE: hiera must have: service::configuration::use_dev_pkgs: true
    include graphoid::packages
    include mathoid::packages
    include trendingedits::packages
}

ensure_packages(['mariadb-client', 'mariadb-server'])

# FIXME should be upstreamed to operations/puppet.git as contint::packages::dev
package { [
    'pkg-config',
    ]:
    ensure => present,
}

# For mediawiki/services, they use `nc` to check Kafka
ensure_packages(['netcat-openbsd'])

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
