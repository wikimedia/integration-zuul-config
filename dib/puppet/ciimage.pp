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
include jenkins::common

include contint::slave_scripts
include contint::packages::base
include contint::composer
include contint::php

include ::profile::zuul::cloner

package { 'cron':
    ensure => present,
}
class { '::profile::ci::hhvm':
    require => Package['cron'],
}

include contint::packages::javascript
include contint::packages::apt
include contint::packages::php

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

include ::profile::phabricator::arcanist

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

# Overrides
class standard {

}
# Safe defaults
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

include contint::packages::doxygen
include contint::packages::java
include contint::packages::python

# Qunit/Selenium related
include profile::ci::browsers


# FIXME: hack, our manifests no more ship libapache2-mod-php{5,7}
# See T144802
# First, we really don't want PHP 5.
apache::mod_conf { 'php5':
    ensure => 'absent',
}
package { 'libapache2-mod-php5':
    ensure => 'absent',
}
class { 'apache::mod::php7':
    ensure  => 'present',
    require => [
      Apache::Mod_conf['php5'],
      Package['libapache2-mod-php5'],
    ],
}


# For Selenium jobs video recording (T113520)
require_package('libav-tools')

class { 'profile::ci::worker_localhost':
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
# run.
# Used to be in services::packages but that is no more supported until a
# solution is found in operations/puppet.git

# graphoid
require_package([
    'libcairo2', 'libgif4', 'libjpeg62-turbo', 'libpango1.0-0',
    'libcairo2-dev', 'libgif-dev', 'libpango1.0-dev', 'libjpeg62-turbo-dev',
])

# mathoid
require_package([
    'librsvg2-2',
    'librsvg2-dev',
])

# trendingedits
require_package([
    'librdkafka++1', 'librdkafka1',
    'librdkafka-dev',
])

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
    require => Package['varnish'],
    enable  => false,
}
# end contint::packages::ops
