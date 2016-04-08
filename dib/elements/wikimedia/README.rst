Bootstrap and run operations/puppet.git in an image

Based on OpenStack 'puppet' element.

DIB_WIKIMEDIA_PUPPET_SOURCE directory holding puppet manifests. Applies:
'bootstrap.pp' to setup hiera
'aptconf.pp' for apt configuration
'ciimage.pp' which hold the rest of puppet

DIB_WIKIMEDIA_PUPPET_DEST directory in the image. Default: /puppet
