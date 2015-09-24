# ciimage.pp
#
# Use operations/puppet.git classes to build our CI image.

include apt
include contint::packages::base
include contint::packages::python
include contint::packages::ops
