Usage on labs instance:

    pip install --user -r requirements.txt
    export PATH=$PATH:~/.local/bin
    ./build_image.sh

You can speed it up next run by reusing debootstrap cache:

   DIB_DEBIAN_USE_DEBOOTSTRAP_CACHE=1 ./build_image.sh

More aggressively:

   DIB_OFFLINE=1 ./build_image.sh

And maybe you will have a qcow2 image build!


See upstream documentation:
http://docs.openstack.org/developer/diskimage-builder/
