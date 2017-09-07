# ciimage.pp
#
# Use operations/puppet.git classes to build our CI image.

$realm = 'labs'
$labsproject = 'contintcloud'

# Should have run aptconf.pp first.

require_package('git')
# We have jobs compiling native packages for NodeJs, Python, Ruby..
require_package('build-essential')

# Invokes apt before anything invokes apt::*
class { '::apt':
    use_proxy => false,
}

# Jenkins provision jre by itself but it sounds better to have it already in
# the  image. T126246.
include jenkins::slave::requisites

include contint::slave_scripts
include contint::packages::base
include contint::composer
include contint::php

include zuul

include mediawiki::packages::php5

package { 'cron':
    ensure => present,
}
if os_version('debian >= jessie') {
    class { '::contint::hhvm':
        require => Package['cron'],
    }
}

include contint::packages::javascript
include contint::packages::apt
include contint::packages::php

if os_version('debian == jessie') {
    apt::repository { 'aptly-integration-php55':
        uri        => 'https://integration-aptly.wmflabs.org/repo/',
        dist       => 'jessie-integration',
        components => 'php55',
        source     => false,
        trust_repo => true,
    }
    package { [
        'php5.5-cli',
        'php5.5-common',
        'php5.5-curl',
        'php5.5-dev',
        'php5.5-gd',
        'php5.5-gmp',
        'php5.5-intl',
        'php5.5-ldap',
        'php5.5-mbstring',
        'php5.5-mcrypt',
        'php5.5-mysql',
        'php5.5-redis',
        'php5.5-sqlite3',
        'php5.5-tidy',
        'php5.5-xsl',
        ]: ensure => present,
        require   => [
          Apt::Repository['aptly-integration-php55'],
          Exec['apt-get update'],
        ],
    }
}

# MediaWiki PHPunit under Zend 5.5 can uses 2GBytes. An attempt to proc_open()
# invokes fork() which clone the Virtual Memory. Although it is copy-on-write,
# Linux still check whether the system will be able to honor a full allocation.
# Allow the Linux memory manager to overcommit memory.
#
# https://phabricator.wikimedia.org/T125050#3153574
# https://www.kernel.org/doc/Documentation/vm/overcommit-accounting
sysctl::parameters { 'vm.overcommit_memory':
    values => { 'vm.overcommit_memory' => 1 },
}

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
    service { 'varnish':
        require  => Package['varnish'],
        enable => false,
    }
}
# end contint::packages::ops
