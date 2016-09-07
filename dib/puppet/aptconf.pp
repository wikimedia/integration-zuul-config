$realm = 'labs'
$labsproject = 'contintcloud'

class { '::apt': }
include contint::packages::apt
