# bootstrap.pp

# Puppet dependency of /etc/puppet/hiera.yaml
package { 'puppetmaster-common':
    ensure => present,
}

# Have a basic hiera lookup hierarchy. Required by various classes from
# operations/puppet.git
class { '::puppetmaster::hiera':
    source => 'puppet:///modules/puppetmaster/labs.hiera.yaml',
}
