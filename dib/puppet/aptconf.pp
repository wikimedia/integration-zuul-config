$realm = 'labs'
$labsproject = 'contintcloud'

require_package('apt-transport-https')

class { '::apt': }
include contint::packages::apt
