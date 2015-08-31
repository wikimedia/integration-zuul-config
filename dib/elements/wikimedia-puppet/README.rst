Bootstrap and run operations/puppet.git in an image

Based on OpenStack 'puppet' element.

DIB_WIKIMEDIA_PUPPET_SOURCE directory holding puppet manifests. First apply
'bootstrap.pp' then 'ciimage.pp'
DIB_WIKIMEDIA_PUPPET_DEST directory in the image. Default: /puppet
