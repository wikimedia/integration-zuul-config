# bootstrap.pp

# Puppet dependency of /etc/puppet/hiera.yaml
package { 'puppetmaster-common':
    ensure => present,
}

# Similar to puppetmaster::hiera
file { '/etc/puppet/hiera.yaml':
    content => ':backends:
  - nuyaml
:nuyaml:
  :datadir: /etc/puppet/hieradata
:hierarchy:
  - "labs/%{::labsproject}/common"
  - "labs"
  - "common"
',
    require => Package['puppetmaster-common'],
}
require_package('puppetmaster-common')
