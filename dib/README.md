Usage on labs instance:

    pip install --user -r requirements.txt
    export PATH=$PATH:~/.local/bin
    ./build_image.py

You can speed it up next run by reusing debootstrap cache:

   DIB_DEBIAN_USE_DEBOOTSTRAP_CACHE=1 ./build_image.py

More aggressively:

   DIB_OFFLINE=1 ./build_image.py

And maybe you will have a qcow2 image build!
